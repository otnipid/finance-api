import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from src import crud, models, schemas

# Account CRUD Tests
def test_create_account(db_session: Session):
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
    account = crud.create_account(db_session, schemas.AccountCreate(**account_data))
    
    assert account.id == "test_acc_123"
    assert account.name == "Test Account"
    assert account.type == "checking"
    assert account.balance == 1000.00

def test_get_account(db_session: Session):
    """Test retrieving an account"""
    # Create a test account
    account = models.Account(
        id="test_acc_123",
        name="Test Account",
        type="checking"
    )
    db_session.add(account)
    db_session.commit()
    
    # Retrieve the account
    db_account = crud.get_account(db_session, "test_acc_123")
    assert db_account is not None
    assert db_account.name == "Test Account"

def test_update_account(db_session: Session):
    """Test updating an account"""
    # Create a test account
    account = models.Account(
        id="test_acc_123",
        name="Old Name",
        type="checking"
    )
    db_session.add(account)
    db_session.commit()
    
    # Update the account
    update_data = {"name": "New Name", "balance": 2000.00}
    updated_account = crud.update_account(
        db_session, 
        "test_acc_123", 
        schemas.AccountUpdate(**update_data)
    )
    
    assert updated_account is not None
    assert updated_account.name == "New Name"
    assert updated_account.balance == 2000.00

def test_delete_account(db_session: Session):
    """Test deleting an account"""
    # Create a test account
    account = models.Account(
        id="test_acc_123",
        name="Test Account",
        type="checking"
    )
    db_session.add(account)
    db_session.commit()
    
    # Delete the account
    deleted_account = crud.delete_account(db_session, "test_acc_123")
    assert deleted_account is not None
    
    # Verify it's gone
    assert crud.get_account(db_session, "test_acc_123") is None

# Transaction CRUD Tests
def test_create_transaction(db_session: Session):
    """Test creating a transaction"""
    # Create an account first
    account = models.Account(
        id="test_acc_123",
        name="Test Account",
        type="checking"
    )
    db_session.add(account)
    db_session.commit()
    
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
        db_session, 
        schemas.TransactionCreate(**transaction_data)
    )
    
    assert transaction.id == "test_txn_123"
    assert transaction.amount == 100.00
    assert transaction.account_id == "test_acc_123"

def test_get_transactions_with_filters(db_session: Session):
    """Test getting transactions with various filters"""
    # Create test data
    account1 = models.Account(id="acc1", name="Account 1", type="checking")
    account2 = models.Account(id="acc2", name="Account 2", type="savings")
    db_session.add_all([account1, account2])
    
    # Create transactions with different dates
    transactions = [
        models.Transaction(
            id=f"txn{i}",
            account_id="acc1",
            posted_date=datetime(2023, 10, i, 12, 0, 0, tzinfo=timezone.utc),
            amount=float(i * 10),
            description=f"Transaction {i}"
        ) for i in range(1, 6)
    ]
    db_session.add_all(transactions)
    db_session.commit()
    
    # Test filtering by account_id
    acc1_txns = crud.get_transactions(db_session, account_id="acc1")
    assert len(acc1_txns) == 5
    
    # Test date range filter
    start_date = datetime(2023, 10, 2, tzinfo=timezone.utc)
    end_date = datetime(2023, 10, 4, tzinfo=timezone.utc)
    filtered_txns = crud.get_transactions(
        db_session,
        start_date=start_date,
        end_date=end_date
    )
    assert len(filtered_txns) == 3  # Should include txn2, txn3, txn4
    
    # Test ordering (should be most recent first)
    assert filtered_txns[0].id == "txn4"
    assert filtered_txns[-1].id == "txn2"

def test_update_transaction(db_session: Session):
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
    db_session.add_all([account, transaction])
    db_session.commit()
    
    # Update the transaction
    update_data = {
        "description": "Updated Description",
        "amount": 200.00
    }
    updated = crud.update_transaction(
        db_session,
        "txn1",
        schemas.TransactionUpdate(**update_data)
    )
    
    assert updated is not None
    assert updated.description == "Updated Description"
    assert updated.amount == 200.00

def test_delete_transaction(db_session: Session):
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
    db_session.add_all([account, transaction])
    db_session.commit()
    
    # Delete the transaction
    deleted = crud.delete_transaction(db_session, "txn1")
    assert deleted is not None
    
    # Verify it's gone
    assert crud.get_transaction(db_session, "txn1") is None

# Budget Category CRUD Tests
def test_budget_category_crud(db_session: Session):
    """Test all budget category CRUD operations"""
    # Create
    category = crud.create_budget_category(
        db_session,
        schemas.BudgetCategoryCreate(name="Groceries", monthly_limit=500.00)
    )
    assert category.id is not None
    assert category.name == "Groceries"
    
    # Read
    categories = crud.get_budget_categories(db_session)
    assert len(categories) == 1
    assert categories[0].name == "Groceries"
    
    # Update
    updated = crud.update_budget_category(
        db_session,
        category.id,
        schemas.BudgetCategoryCreate(name="Groceries", monthly_limit=600.00)
    )
    assert updated.monthly_limit == 600.00
    
    # Delete
    deleted = crud.delete_budget_category(db_session, category.id)
    assert deleted is not None
    assert crud.get_budget_category(db_session, category.id) is None

# Savings Bucket CRUD Tests
def test_savings_bucket_crud(db_session: Session):
    """Test all savings bucket CRUD operations"""
    # Create
    bucket = crud.create_savings_bucket(
        db_session,
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
    buckets = crud.get_savings_buckets(db_session)
    assert len(buckets) == 1
    assert buckets[0].target_amount == 10000.00
    
    # Update
    updated = crud.update_savings_bucket(
        db_session,
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
    deleted = crud.delete_savings_bucket(db_session, bucket.id)
    assert deleted is not None
    assert crud.get_savings_bucket(db_session, bucket.id) is None
