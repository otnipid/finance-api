from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
def test():
    return {"message": "API is running"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/accounts/", response_model=schemas.Account)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    return crud.create_account(db, account)

@app.get("/accounts/", response_model=list[schemas.Account])
def read_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_accounts(db, skip=skip, limit=limit)

@app.get("/accounts/{account_id}", response_model=schemas.Account)
def read_account(account_id: int, db: Session = Depends(get_db)):
    db_account = crud.get_account(db, account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@app.delete("/accounts/{account_id}", response_model=schemas.Account)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    db_account = crud.delete_account(db, account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@app.post("/transactions/", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db, transaction)

@app.get("/transactions/", response_model=list[schemas.Transaction])
def read_transactions(account_id: int = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if account_id is not None:
        return crud.get_transactions_by_account(db, account_id=account_id, skip=skip, limit=limit)
    return crud.get_transactions(db, skip=skip, limit=limit)

@app.delete("/transactions/{transaction_id}", response_model=schemas.Transaction)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = crud.delete_transaction(db, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@app.post("/budget-categories/", response_model=schemas.BudgetCategory)
def create_budget_category(category: schemas.BudgetCategoryCreate, db: Session = Depends(get_db)):
    return crud.create_budget_category(db, category)

@app.get("/budget-categories/", response_model=list[schemas.BudgetCategory])
def read_budget_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_budget_categories(db, skip=skip, limit=limit)

@app.delete("/budget-categories/{category_id}", response_model=schemas.BudgetCategory)
def delete_budget_category(category_id: int, db: Session = Depends(get_db)):
    db_category = crud.delete_budget_category(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Budget category not found")
    return db_category

@app.post("/savings-buckets/", response_model=schemas.SavingsBucket)
def create_savings_bucket(bucket: schemas.SavingsBucketCreate, db: Session = Depends(get_db)):
    return crud.create_savings_bucket(db, bucket)

@app.get("/savings-buckets/", response_model=list[schemas.SavingsBucket])
def read_savings_buckets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_savings_buckets(db, skip=skip, limit=limit)

@app.delete("/savings-buckets/{bucket_id}", response_model=schemas.SavingsBucket)
def delete_savings_bucket(bucket_id: int, db: Session = Depends(get_db)):
    db_bucket = crud.delete_savings_bucket(db, bucket_id)
    if db_bucket is None:
        raise HTTPException(status_code=404, detail="Savings bucket not found")
    return db_bucket