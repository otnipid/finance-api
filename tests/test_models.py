import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import IntegrityError

from src.models import Account, Transaction, BudgetCategory, SavingsBucket

def test_create_account(db):
    """Test creating an account with valid data"""
    account = Account(
        id="test_acc_123",
        name="Test Account",
        type="checking",
        currency="USD",
        balance=1000.00,
        org_name="Test Bank",
        url="https://test-bank.com"
    )
    db.add(account)
    db.commit()
    
    # Verify the account was created with correct data
    db_account = db.query(Account).filter(Account.id == "test_acc_123").first()
    assert db_account is not None
    assert db_account.name == "Test Account"
    assert db_account.type == "checking"
    assert db_account.balance == 1000.00
    assert db_account.last_updated is not None

def test_create_transaction(db, test_account_data):
    """Test creating a transaction with valid data"""
    # First create an account
    account = Account(**test_account_data)
    db.add(account)
    db.commit()
    
    # Create a transaction
    transaction = Transaction(
        id="test_txn_123",
        account_id=account.id,
        posted_date=datetime.now(timezone.utc),
        amount=100.00,
        description="Test Transaction",
        memo="Test memo",
        payee="Test Payee",
        pending=False
    )
    db.add(transaction)
    db.commit()
    
    # Verify the transaction was created with correct data
    db_transaction = db.query(Transaction).filter(Transaction.id == "test_txn_123").first()
    assert db_transaction is not None
    assert db_transaction.amount == 100.00
    assert db_transaction.account_id == account.id
    assert db_transaction.created_at is not None

def test_transaction_relationships(db, test_account_data):
    """Test the relationship between Account and Transaction"""
    # Create an account
    account = Account(**test_account_data)
    db.add(account)
    db.commit()
    
    # Create a transaction for the account
    transaction = Transaction(
        id="test_txn_rel_123",
        account_id=account.id,
        posted_date=datetime.now(timezone.utc),
        amount=50.00,
        description="Test Relationship"
    )
    db.add(transaction)
    db.commit()
    
    # Test the relationship
    db_transaction = db.query(Transaction).filter(Transaction.id == "test_txn_rel_123").first()
    assert db_transaction.account.id == account.id
    assert db_transaction.account.name == account.name

def test_budget_category_creation(db):
    """Test creating a budget category"""
    category = BudgetCategory(
        name="Test Category",
        monthly_limit=1000.00
    )
    db.add(category)
    db.commit()
    
    db_category = db.query(BudgetCategory).filter(BudgetCategory.name == "Test Category").first()
    assert db_category is not None
    assert db_category.monthly_limit == 1000.00
    assert db_category.created_at is not None

def test_savings_bucket_creation(db):
    """Test creating a savings bucket"""
    bucket = SavingsBucket(
        name="Test Savings",
        target_amount=5000.00,
        current_amount=1000.00,
        goal_date=datetime.now(timezone.utc).date() + timedelta(days=365)
    )
    db.add(bucket)
    db.commit()
    
    db_bucket = db.query(SavingsBucket).filter(SavingsBucket.name == "Test Savings").first()
    assert db_bucket is not None
    assert db_bucket.target_amount == 5000.00
    assert db_bucket.current_amount == 1000.00
    assert db_bucket.created_at is not None
