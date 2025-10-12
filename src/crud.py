from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from datetime import datetime
from src import models, schemas

def create_account(db: Session, account: schemas.AccountCreate) -> models.Account:
    """Create a new account"""
    db_account = models.Account(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_accounts(db: Session, skip: int = 0, limit: int = 100) -> List[models.Account]:
    """Get all accounts with pagination"""
    return db.query(models.Account).offset(skip).limit(limit).all()

def get_account(db: Session, account_id: str) -> Optional[models.Account]:
    """Get an account by ID"""
    return db.query(models.Account).filter(models.Account.id == account_id).first()

def update_account(
    db: Session, 
    account_id: str, 
    account_update: schemas.AccountUpdate
) -> Optional[models.Account]:
    """Update an account"""
    db_account = get_account(db, account_id)
    if db_account:
        update_data = account_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_account, key, value)
        db_account.last_updated = datetime.utcnow()
        db.commit()
        db.refresh(db_account)
    return db_account

def delete_account(db: Session, account_id: str) -> Optional[models.Account]:
    """Delete an account"""
    db_account = get_account(db, account_id)
    if db_account:
        db.delete(db_account)
        db.commit()
    return db_account

def create_transaction(db: Session, transaction: schemas.TransactionCreate) -> models.Transaction:
    """Create a new transaction"""
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    account_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[models.Transaction]:
    """Get transactions with optional filtering"""
    query = db.query(models.Transaction)
    
    if account_id:
        query = query.filter(models.Transaction.account_id == account_id)
    
    if start_date:
        query = query.filter(models.Transaction.posted_date >= start_date)
    
    if end_date:
        query = query.filter(models.Transaction.posted_date <= end_date)
    
    return query.order_by(desc(models.Transaction.posted_date)).offset(skip).limit(limit).all()

def get_transaction(db: Session, transaction_id: str) -> Optional[models.Transaction]:
    """Get a transaction by ID"""
    return db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

def update_transaction(
    db: Session, 
    transaction_id: str, 
    transaction_update: schemas.TransactionUpdate
) -> Optional[models.Transaction]:
    """Update a transaction"""
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction:
        update_data = transaction_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_transaction, key, value)
        db.commit()
        db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: str) -> Optional[models.Transaction]:
    """Delete a transaction"""
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
    return db_transaction

# Budget Categories
def create_budget(
    db: Session, 
    budget: schemas.BudgetCategoryCreate
) -> models.BudgetCategory:
    """Create a new budget category"""
    db_budget = models.BudgetCategory(**budget.dict())
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def get_budgets(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[models.BudgetCategory]:
    """Get all budget categories with pagination"""
    return db.query(models.BudgetCategory).offset(skip).limit(limit).all()

def get_budget(
    db: Session, 
    budget_id: int
) -> Optional[models.BudgetCategory]:
    """Get a budget category by ID"""
    return db.query(models.BudgetCategory).filter(models.BudgetCategory.id == budget_id).first()

def update_budget(
    db: Session, 
    budget_id: int, 
    budget: schemas.BudgetCategoryUpdate
) -> Optional[models.BudgetCategory]:
    """Update a budget category"""
    db_budget = get_budget(db, budget_id=budget_id)
    if db_budget:
        update_data = budget.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_budget, key, value)
        db.commit()
        db.refresh(db_budget)
    return db_budget

def delete_budget(
    db: Session, 
    budget_id: int
) -> Optional[models.BudgetCategory]:
    """Delete a budget category"""
    db_budget = get_budget(db, budget_id=budget_id)
    if db_budget:
        db.delete(db_budget)
        db.commit()
    return db_budget

# Savings Buckets
def create_savings_bucket(
    db: Session, 
    bucket: schemas.SavingsBucketCreate
) -> models.SavingsBucket:
    """Create a new savings bucket"""
    db_bucket = models.SavingsBucket(**bucket.dict())
    db.add(db_bucket)
    db.commit()
    db.refresh(db_bucket)
    return db_bucket

def get_savings_buckets(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[models.SavingsBucket]:
    """Get all savings buckets"""
    return db.query(models.SavingsBucket).offset(skip).limit(limit).all()

def get_savings_bucket(
    db: Session, 
    bucket_id: int
) -> Optional[models.SavingsBucket]:
    """Get a savings bucket by ID"""
    return db.query(models.SavingsBucket).filter(models.SavingsBucket.id == bucket_id).first()

def update_savings_bucket(
    db: Session, 
    bucket_id: int, 
    bucket_update: schemas.SavingsBucketUpdate
) -> Optional[models.SavingsBucket]:
    """Update a savings bucket"""
    db_bucket = get_savings_bucket(db, bucket_id)
    if db_bucket is None:
        return None
        
    update_data = bucket_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_bucket, key, value)
    
    db.commit()
    db.refresh(db_bucket)
    return db_bucket

def delete_savings_bucket(db: Session, bucket_id: int) -> Optional[models.SavingsBucket]:
    """Delete a savings bucket"""
    db_bucket = get_savings_bucket(db, bucket_id)
    if db_bucket:
        db.delete(db_bucket)
        db.commit()
    return db_bucket