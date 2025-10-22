from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from datetime import datetime

from ..database import get_db
from ..models import Account, Transaction
from ..services.simplefin import SimpleFinClient, SimpleFinError

router = APIRouter(prefix="/sync", tags=["sync"])
logger = logging.getLogger(__name__)

@router.post("/simplefin", status_code=status.HTTP_200_OK)
async def sync_simplefin(
    days_back: int = 30,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Sync accounts and transactions from SimpleFIN.
    
    Args:
        days_back: Number of days of transactions to sync
        db: Database session
        
    Returns:
        Dict with sync results
    """
    try:
        # Initialize SimpleFIN client
        client = SimpleFinClient()
        
        # Get accounts and transactions
        accounts = client.get_accounts(include_transactions=True, days_back=days_back)
        transactions = client.get_transactions(days_back=days_back)
        
        # Process accounts
        account_count = 0
        for account in accounts:
            account_data = {
                'id': account['id'],
                'name': account.get('name', ''),
                'currency': account.get('currency'),
                'type': account.get('type'),
                'balance': float(account.get('balance', 0)),
                'org_name': account.get('org', {}).get('name'),
                'url': account.get('org', {}).get('url')
            }
            
            # Upsert account
            db_account = db.query(Account).filter(Account.id == account_data['id']).first()
            if db_account:
                # Update existing account
                for key, value in account_data.items():
                    setattr(db_account, key, value)
            else:
                # Create new account
                db_account = Account(**account_data)
                db.add(db_account)
            
            account_count += 1
        
        # Process transactions
        transaction_count = 0
        for tx in transactions:
            tx_data = {
                'id': tx['id'],
                'account_id': tx['account_id'],
                'posted_date': datetime.fromtimestamp(tx['posted']),
                'amount': float(tx.get('amount', 0)),
                'description': tx.get('description'),
                'memo': tx.get('memo'),
                'pending': tx.get('pending', False),
                'payee': tx.get('payee'),
                'category': tx.get('category', 'Uncategorized')
            }
            
            # Upsert transaction
            db_tx = db.query(Transaction).filter(Transaction.id == tx_data['id']).first()
            if db_tx:
                # Update existing transaction
                for key, value in tx_data.items():
                    setattr(db_tx, key, value)
            else:
                # Create new transaction
                db_tx = Transaction(**tx_data)
                db.add(tx_data)
            
            transaction_count += 1
        
        # Commit all changes
        db.commit()
        
        return {
            "status": "success",
            "accounts_processed": account_count,
            "transactions_processed": transaction_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except SimpleFinError as e:
        logger.error(f"SimpleFIN sync error: {str(e)}", exc_info=True)
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