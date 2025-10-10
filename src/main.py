from fastapi import FastAPI, Depends, HTTPException, Request, Body, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import models, schemas, crud
from database import SessionLocal, engine, Base
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Account Endpoints
@app.post("/api/accounts/", response_model=schemas.Account, status_code=status.HTTP_201_CREATED)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    """Create a new account"""
    db_account = crud.get_account(db, account_id=account.id)
    if db_account:
        raise HTTPException(status_code=400, detail="Account already exists")
    return crud.create_account(db=db, account=account)

@app.get("/api/accounts/", response_model=List[schemas.Account])
def read_accounts(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all accounts with pagination"""
    return crud.get_accounts(db, skip=skip, limit=limit)

@app.get("/api/accounts/{account_id}", response_model=schemas.Account)
def read_account(account_id: str, db: Session = Depends(get_db)):
    """Get a specific account by ID"""
    db_account = crud.get_account(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@app.put("/api/accounts/{account_id}", response_model=schemas.Account)
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

@app.delete("/api/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: str, db: Session = Depends(get_db)):
    """Delete an account"""
    db_account = crud.get_account(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    crud.delete_account(db=db, account_id=account_id)
    return None

# Transaction Endpoints
@app.post("/api/transactions/", response_model=schemas.Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: schemas.TransactionCreate, 
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    # Verify account exists
    if not crud.get_account(db, account_id=transaction.account_id):
        raise HTTPException(status_code=400, detail="Account not found")
    return crud.create_transaction(db=db, transaction=transaction)

@app.get("/api/transactions/", response_model=List[schemas.Transaction])
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

@app.get("/api/transactions/{transaction_id}", response_model=schemas.Transaction)
def read_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """Get a specific transaction by ID"""
    db_transaction = crud.get_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@app.put("/api/transactions/{transaction_id}", response_model=schemas.Transaction)
def update_transaction(
    transaction_id: str, 
    transaction: schemas.TransactionUpdate, 
    db: Session = Depends(get_db)
):
    """Update a transaction"""
    db_transaction = crud.get_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return crud.update_transaction(db=db, transaction_id=transaction_id, transaction_update=transaction)

@app.delete("/api/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """Delete a transaction"""
    db_transaction = crud.get_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    crud.delete_transaction(db=db, transaction_id=transaction_id)
    return None

# Budget Category Endpoints
@app.post("/api/budget-categories/", response_model=schemas.BudgetCategory, status_code=status.HTTP_201_CREATED)
def create_budget_category(
    category: schemas.BudgetCategoryCreate, 
    db: Session = Depends(get_db)
):
    """Create a new budget category"""
    return crud.create_budget_category(db=db, category=category)

@app.get("/api/budget-categories/", response_model=List[schemas.BudgetCategory])
def read_budget_categories(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all budget categories"""
    return crud.get_budget_categories(db=db, skip=skip, limit=limit)

# Savings Bucket Endpoints
@app.post("/api/savings-buckets/", response_model=schemas.SavingsBucket, status_code=status.HTTP_201_CREATED)
def create_savings_bucket(
    bucket: schemas.SavingsBucketCreate, 
    db: Session = Depends(get_db)
):
    """Create a new savings bucket"""
    return crud.create_savings_bucket(db=db, bucket=bucket)

@app.get("/api/savings-buckets/", response_model=List[schemas.SavingsBucket])
def read_savings_buckets(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all savings buckets"""
    return crud.get_savings_buckets(db=db, skip=skip, limit=limit)

# Health Check Endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}