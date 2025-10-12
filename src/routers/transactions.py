from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, crud
from ..database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: schemas.TransactionCreate, 
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    # Verify account exists
    if not crud.get_account(db, account_id=transaction.account_id):
        raise HTTPException(status_code=400, detail="Account not found")
    return crud.create_transaction(db=db, transaction=transaction)

@router.get("/", response_model=List[schemas.Transaction])
def read_transactions(
    account_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get transactions with optional filtering"""
    return crud.get_transactions(
        db=db, 
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip, 
        limit=limit
    )

@router.get("/{transaction_id}", response_model=schemas.Transaction)
def read_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """Get a specific transaction by ID"""
    db_transaction = crud.get_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@router.put("/{transaction_id}", response_model=schemas.Transaction)
def update_transaction(
    transaction_id: str, 
    transaction: schemas.TransactionUpdate, 
    db: Session = Depends(get_db)
):
    """Update a transaction"""
    db_transaction = crud.get_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return crud.update_transaction(
        db=db, 
        transaction_id=transaction_id, 
        transaction_update=transaction
    )

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """Delete a transaction"""
    db_transaction = crud.get_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    crud.delete_transaction(db=db, transaction_id=transaction_id)
    return None
