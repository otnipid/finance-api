from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud
from ..database import get_db
from ..models import Account, Transaction
from ..services.simplefin import SimpleFinClient, SimpleFinError
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/simplefin", status_code=status.HTTP_200_OK)
async def sync_simplefin(
    days_back: int = 30,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Sync accounts and transactions from SimpleFIN.
    
    Only adds new accounts and transactions that don't already exist in the database.
    Existing records will not be modified.
    """
    try:
        logger.info("Starting SimpleFIN sync...")
        # Initialize SimpleFIN client
        client = SimpleFinClient()
        
        # Get accounts and transactions
        accounts = client.get_accounts(include_transactions=True, days_back=days_back)
        logger.info(f"Retrieved {len(accounts)} accounts from SimpleFIN")
        
        # Get all existing account IDs for quick lookup
        existing_accounts = db.query(Account).all()
        existing_account_ids = {acc.id for acc in existing_accounts}
        logger.info(f"Found {len(existing_account_ids)} existing accounts in database")
        
        # Process accounts - only add new ones
        new_account_count = 0
        for i, account in enumerate(accounts, 1):
            account_id = account.get('id')
            if not account_id:
                logger.warning(f"Account at index {i} has no ID, skipping")
                continue
                
            if account_id in existing_account_ids:
                logger.debug(f"Account {account_id} already exists, skipping")
                continue
                
            # Prepare account data
            account_data = {
                'id': account_id,
                'name': account.get('name', ''),
                'currency': account.get('currency'),
                'type': account.get('type'),
                'balance': float(account.get('balance', 0)),
                'org_name': account.get('org', {}).get('name'),
                'url': account.get('org', {}).get('url')
            }
            
            # Add new account
            db_account = Account(**account_data)
            db.add(db_account)
            logger.info(f"Adding new account: {account_data}")
            new_account_count += 1
        
        # Commit new accounts first to ensure foreign key constraints are satisfied
        if new_account_count > 0:
            db.commit()
            logger.info(f"Committed {new_account_count} new accounts to database")
        
        # Get all existing transactions for quick lookup
        existing_tx_ids = {tx[0] for tx in db.query(Transaction.id).all()}
        logger.info(f"Found {len(existing_tx_ids)} existing transactions in database")
        
        # Process transactions - only add new ones
        new_transaction_count = 0
        skipped_transactions = 0
        transactions = client.get_transactions(days_back=days_back)
        
        for i, tx in enumerate(transactions, 1):
            tx_id = tx.get('id')
            account_id = tx.get('account_id')
            
            if not tx_id:
                logger.warning(f"Transaction at index {i} has no ID, skipping")
                skipped_transactions += 1
                continue
                
            if not account_id:
                logger.warning(f"Transaction {tx_id} has no account ID, skipping")
                skipped_transactions += 1
                continue
                
            # Check if transaction already exists
            if tx_id in existing_tx_ids:
                logger.debug(f"Transaction {tx_id} already exists, skipping")
                skipped_transactions += 1
                continue
            
            # Check if account exists
            if account_id not in existing_account_ids:
                logger.warning(f"Account {account_id} not found for transaction {tx_id}, skipping")
                skipped_transactions += 1
                continue
            
            try:
                # Prepare transaction data
                tx_data = {
                    'id': tx_id,
                    'account_id': account_id,
                    'posted_date': datetime.fromtimestamp(tx['posted']),
                    'amount': float(tx.get('amount', 0)),
                    'description': tx.get('description'),
                    'memo': tx.get('memo'),
                    'pending': tx.get('pending', False),
                    'payee': tx.get('payee'),
                    'category': tx.get('category', 'Uncategorized')
                }
                
                # Add new transaction
                db_tx = Transaction(**tx_data)
                db.add(db_tx)
                new_transaction_count += 1
                logger.info(f"Adding new transaction: {tx_data}")
                
                # Batch commit transactions
                if new_transaction_count % 10 == 0:
                    db.commit()
                    logger.debug(f"Committed batch of 10 transactions")
                    
            except Exception as e:
                logger.error(f"Error processing transaction {tx_id}: {str(e)}", exc_info=True)
                db.rollback()
                skipped_transactions += 1
                continue
        
        # Final commit for any remaining transactions
        if new_transaction_count > 0:
            db.commit()
            logger.info(f"Committed final batch of {new_transaction_count % 10} transactions")
        
        logger.info(f"Sync completed. Added {new_account_count} accounts and {new_transaction_count} transactions. Skipped {skipped_transactions} transactions.")
        
        return {
            "status": "success",
            "new_accounts_added": new_account_count,
            "new_transactions_added": new_transaction_count,
            "skipped_transactions": skipped_transactions,
            "total_accounts": len(existing_accounts) + new_account_count,
            "total_transactions": len(existing_tx_ids) + new_transaction_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except SimpleFinError as e:
        logger.error(f"SimpleFIN sync error: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to sync with SimpleFIN: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during SimpleFIN sync: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during sync"
        )