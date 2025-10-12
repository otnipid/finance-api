from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud
from ..database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Account, status_code=status.HTTP_201_CREATED)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    """Create a new account"""
    db_account = crud.get_account(db, account_id=account.id)
    if db_account:
        raise HTTPException(status_code=400, detail="Account already exists")
    return crud.create_account(db=db, account=account)

@router.get("/", response_model=List[schemas.Account])
def read_accounts(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all accounts with pagination"""
    return crud.get_accounts(db, skip=skip, limit=limit)

@router.get("/{account_id}", response_model=schemas.Account)
def read_account(account_id: str, db: Session = Depends(get_db)):
    """Get a specific account by ID"""
    db_account = crud.get_account(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@router.put("/{account_id}", response_model=schemas.Account)
def update_account(
    account_id: str, 
    account: schemas.AccountUpdate, 
    db: Session = Depends(get_db)
):
    """Update an account"""
    db_account = crud.get_account(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return crud.update_account(db=db, account_id=account_id, account_update=account)

@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: str, db: Session = Depends(get_db)):
    """Delete an account"""
    db_account = crud.get_account(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    crud.delete_account(db=db, account_id=account_id)
    return None
