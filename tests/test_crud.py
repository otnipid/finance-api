import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from src import crud, models, schemas

# Account CRUD Tests
def test_create_account(db: Session):
    """Test creating an account"""
    account_data = {
        "id": "test_acc_123",
        "name": "Test Account",
        "type": "checking",
        "currency": "USD",
        "balance": 1000.00,
        "org_name": "Test Bank",
        "url": "https://test-bank.com"
    }
    account = crud.create_account(db, schemas.AccountCreate(**account_data))
    
    assert account.id == "test_acc_123"
    assert account.name == "Test Account"
    assert account.type == "checking"
    assert account.balance == 1000.00

def test_get_account(db: Session):
    """Test retrieving an account"""
    # Create a test account
    account = models.Account(
        id="test_acc_123",
        name="Test Account",
        type="checking"
    )
    db.add(account)
    db.commit()
    
    # Retrieve the account
    db_account = crud.get_account(db, "test_acc_123")
    assert db_account is not None
    assert db_account.name == "Test Account"

def test_update_account(db: Session):
    """Test updating an account"""
    # Create a test account
    account = models.Account(
        id="test_acc_123",
        name="Old Name",
        type="checking"
    )
    db.add(account)
    db.commit()
    
    # Update the account
    update_data = {"name": "New Name", "balance": 2000.00}
    updated_account = crud.update_account(
        db, 
        "test_acc_123", 
        schemas.AccountUpdate(**update_data)
    )
    
    assert updated_account is not None
    assert updated_account.name == "New Name"
    assert updated_account.balance == 2000.00

def test_delete_account(db: Session):
    """Test deleting an account"""
    # Create a test account
    account = models.Account(
        id="test_acc_123",
        name="Test Account",
        type="checking"
    )
    db.add(account)
    db.commit()
    
    # Delete the account
    deleted_account = crud.delete_account(db, "test_acc_123")
    assert deleted_account is not None
    
    # Verify it's gone
    assert crud.get_account(db, "test_acc_123") is None

# Transaction CRUD Tests
def test_create_transaction(db: Session):
    """Test creating a transaction"""
    # Create an account first
    account = models.Account(
        id="test_acc_123",
        name="Test Account",
        type="checking"
    )
    db.add(account)
    db.commit()
    
    # Create transaction
    transaction_data = {
        "id": "test_txn_123",
        "account_id": "test_acc_123",
        "posted_date": datetime(2023, 10, 12, 12, 0, 0, tzinfo=timezone.utc),
        "amount": 100.00,
        "description": "Test Transaction",
        "memo": "Test memo",
        "payee": "Test Payee",
        "pending": False
    }
    transaction = crud.create_transaction(
        db, 
        schemas.TransactionCreate(**transaction_data)
    )
    
    assert transaction.id == "test_txn_123"
    assert transaction.amount == 100.00
    assert transaction.account_id == "test_acc_123"

def test_get_transactions_with_filters(db: Session):
    """Test getting transactions with various filters"""
    # Create test data
    account1 = models.Account(id="acc1", name="Account 1", type="checking")
    account2 = models.Account(id="acc2", name="Account 2", type="savings")
    db.add_all([account1, account2])
    
    # Create transactions with different dates
    transactions = [
        models.Transaction(
            id=f"txn{i}",
            account_id="acc1",
            posted_date=datetime(2023, 10, i, 12, 0, 0, tzinfo=timezone.utc),
            amount=float(i * 10),
            description=f"Transaction {i}",
            pending=False
        ) for i in range(1, 6)
    ]
    db.add_all(transactions)
    db.commit()
    
    # Test filtering by account_id
    acc1_txns = crud.get_transactions(db, account_id="acc1")
    assert len(acc1_txns) == 5
    
    # Test date range filter
    start_date = datetime(2023, 10, 2, tzinfo=timezone.utc)
    end_date = datetime(2023, 10, 4, 23, 59, 59, tzinfo=timezone.utc)
    filtered_txns = crud.get_transactions(
        db,
        account_id="acc1",
        start_date=start_date,
        end_date=end_date
    )
    assert len(filtered_txns) == 3  # Should include txn2, txn3, txn4
    
    # Test ordering (should be most recent first)
    assert filtered_txns[0].id == "txn4"
    assert filtered_txns[1].id == "txn3"
    assert filtered_txns[2].id == "txn2"

def test_update_transaction(db: Session):
    """Test updating a transaction"""
    # Create test data
    account = models.Account(id="acc1", name="Account 1", type="checking")
    transaction = models.Transaction(
        id="txn1",
        account_id="acc1",
        posted_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
        amount=100.00,
        description="Old Description"
    )
    db.add_all([account, transaction])
    db.commit()
    
    # Update the transaction
    update_data = {
        "description": "Updated Description",
        "amount": 200.00
    }
    updated = crud.update_transaction(
        db,
        "txn1",
        schemas.TransactionUpdate(**update_data)
    )
    
    assert updated is not None
    assert updated.description == "Updated Description"
    assert updated.amount == 200.00

def test_delete_transaction(db: Session):
    """Test deleting a transaction"""
    # Create test data
    account = models.Account(id="acc1", name="Account 1", type="checking")
    transaction = models.Transaction(
        id="txn1",
        account_id="acc1",
        posted_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
        amount=100.00,
        description="Test Transaction"
    )
    db.add_all([account, transaction])
    db.commit()
    
    # Delete the transaction
    deleted = crud.delete_transaction(db, "txn1")
    assert deleted is not None
    
    # Verify it's gone
    assert crud.get_transaction(db, "txn1") is None

# Budget Category CRUD Tests
def test_budget_category_crud(db: Session):
    """Test all budget category CRUD operations"""
    # Test create
    category_data = {
        "name": "Test Category",
        "monthly_limit": 1000.0
    }
    category = crud.create_budget(db, schemas.BudgetCategoryCreate(**category_data))
    assert category.id is not None
    assert category.name == "Test Category"
    assert category.monthly_limit == 1000.0
    
    # Test read
    db_category = crud.get_budget(db, category.id)
    assert db_category is not None
    assert db_category.name == "Test Category"
    
    # Test update
    update_data = {"name": "Updated Category", "monthly_limit": 1500.0}
    updated_category = crud.update_budget(
        db, 
        category.id, 
        schemas.BudgetCategoryUpdate(**update_data)
    )
    assert updated_category.name == "Updated Category"
    assert updated_category.monthly_limit == 1500.0
    
    # Test delete
    crud.delete_budget(db, category.id)
    assert crud.get_budget(db, category.id) is None

# Savings Bucket CRUD Tests
def test_savings_bucket_crud(db: Session):
    """Test all savings bucket CRUD operations"""
    # Create
    bucket = crud.create_savings_bucket(
        db,
        schemas.SavingsBucketCreate(
            name="Emergency Fund",
            target_amount=10000.00,
            current_amount=1000.00,
            goal_date=datetime(2024, 12, 31, tzinfo=timezone.utc).date()
        )
    )
    assert bucket.id is not None
    assert bucket.name == "Emergency Fund"
    
    # Read
    buckets = crud.get_savings_buckets(db)
    assert len(buckets) == 1
    assert buckets[0].target_amount == 10000.00
    
    # Update
    updated = crud.update_savings_bucket(
        db,
        bucket.id,
        schemas.SavingsBucketCreate(
            name="Emergency Fund",
            target_amount=15000.00,
            current_amount=1000.00,
            goal_date=datetime(2024, 12, 31, tzinfo=timezone.utc).date()
        )
    )
    assert updated.target_amount == 15000.00
    
    # Delete
    deleted = crud.delete_savings_bucket(db, bucket.id)
    assert deleted is not None
    assert crud.get_savings_bucket(db, bucket.id) is None
