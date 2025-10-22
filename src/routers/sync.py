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
    
    Args:
        days_back: Number of days of transactions to sync
        db: Database session
        
    Returns:
        Dict with sync results including counts of new accounts and transactions added
    """
    try:
        # Initialize SimpleFIN client
        client = SimpleFinClient()
        
        # Get accounts and transactions
        accounts = client.get_accounts(include_transactions=True, days_back=days_back)
        transactions = client.get_transactions(days_back=days_back)
        
        # Get all existing account IDs for quick lookup
        existing_account_ids = {account[0] for account in db.query(Account.id).all()}
        
        # Process accounts - only add new ones
        new_account_count = 0
        for account in accounts:
            account_id = account.get('id')
            if not account_id:
                continue
                
            # Skip if account already exists
            if account_id in existing_account_ids:
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
            new_account_count += 1
        
        # Commit new accounts first to ensure foreign key constraints are satisfied
        if new_account_count > 0:
            db.commit()
        
        # Get all existing transaction IDs for quick lookup
        existing_tx_ids = {tx[0] for tx in db.query(Transaction.id).all()}
        
        # Process transactions - only add new ones
        new_transaction_count = 0
        for tx in transactions:
            tx_id = tx.get('id')
            account_id = tx.get('account_id')
            
            # Skip if missing required fields or transaction already exists
            if not all([tx_id, account_id]) or tx_id in existing_tx_ids:
                continue
            
            # Skip if account doesn't exist in our database
            if account_id not in existing_account_ids and account_id not in {
                account.get('id') for account in accounts
                if account.get('id') not in existing_account_ids
            }:
                logger.warning(f"Account {account_id} not found in database or new accounts, skipping transaction {tx_id}")
                continue
            
            # Prepare transaction data
            try:
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
                
                # Batch commit transactions to avoid large transactions
                if new_transaction_count % 100 == 0:
                    db.commit()
                    
            except Exception as e:
                logger.error(f"Error processing transaction {tx_id}: {str(e)}")
                continue
        
        # Final commit for any remaining transactions
        if new_transaction_count % 100 != 0:
            db.commit()
        
        return {
            "status": "success",
            "new_accounts_added": new_account_count,
            "new_transactions_added": new_transaction_count,
            "total_accounts": len(existing_account_ids) + new_account_count,
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