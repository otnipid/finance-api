from sqlalchemy.orm import Session
import models, schemas

def create_account(db: Session, account: schemas.AccountCreate):
    db_account = models.Account(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_accounts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Account).offset(skip).limit(limit).all()

def get_account(db: Session, account_id: int):
    return db.query(models.Account).filter(models.Account.id == account_id).first()

def delete_account(db: Session, account_id: int):
    db_account = get_account(db, account_id)
    if db_account:
        db.delete(db_account)
        db.commit()
    return db_account

def update_account(db: Session, account_id: int, account: schemas.AccountCreate):
    db_account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if db_account:
        for key, value in account.dict().items():
            setattr(db_account, key, value)
        db.commit()
        db.refresh(db_account)
    return db_account

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).order_by(models.Transaction.date.desc()).offset(skip).limit(limit).all()

def get_transactions_by_account(db: Session, account_id: int, skip: int = 0, limit: int = 100):
    return (db.query(models.Transaction)
             .filter(models.Transaction.account_id == account_id)
             .order_by(models.Transaction.date.desc())
             .offset(skip)
             .limit(limit)
             .all())

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionCreate):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if db_transaction:
        for key, value in transaction.dict().items():
            setattr(db_transaction, key, value)
        db.commit()
        db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
    return db_transaction

def create_budget_category(db: Session, category: schemas.BudgetCategoryCreate):
    db_category = models.BudgetCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_budget_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.BudgetCategory).offset(skip).limit(limit).all()

def delete_budget_category(db: Session, category_id: int):
    db_category = db.query(models.BudgetCategory).filter(models.BudgetCategory.id == category_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category

def update_budget_category(db: Session, category_id: int, category: schemas.BudgetCategoryCreate):
    db_category = db.query(models.BudgetCategory).filter(models.BudgetCategory.id == category_id).first()
    if db_category:
        for key, value in category.dict().items():
            setattr(db_category, key, value)
        db.commit()
        db.refresh(db_category)
    return db_category

def create_savings_bucket(db: Session, bucket: schemas.SavingsBucketCreate):
    db_bucket = models.SavingsBucket(**bucket.dict())
    db.add(db_bucket)
    db.commit()
    db.refresh(db_bucket)
    return db_bucket

def get_savings_buckets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SavingsBucket).offset(skip).limit(limit).all()

def delete_savings_bucket(db: Session, bucket_id: int):
    db_bucket = db.query(models.SavingsBucket).filter(models.SavingsBucket.id == bucket_id).first()
    if db_bucket:
        db.delete(db_bucket)
        db.commit()
    return db_bucket

def update_savings_bucket(db: Session, bucket_id: int, bucket: schemas.SavingsBucketCreate):
    db_bucket = db.query(models.SavingsBucket).filter(models.SavingsBucket.id == bucket_id).first()
    if db_bucket:
        for key, value in bucket.dict().items():
            setattr(db_bucket, key, value)
        db.commit()
        db.refresh(db_bucket)
    return db_bucket