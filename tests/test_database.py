import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime, timezone

def test_database_connection(db_session: Session):
    """Test that the database connection is working"""
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1

def test_database_tables_exist(db_session: Session):
    """Verify that all expected tables exist in the database"""
    result = db_session.execute(
        text("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%';
        """)
    )
    tables = {row[0] for row in result.fetchall()}
    
    required_tables = {
        'accounts', 
        'transactions', 
        'budget_categories', 
        'savings_buckets'
    }
    
    missing_tables = required_tables - tables
    assert not missing_tables, f"Missing tables: {missing_tables}"

def test_can_create_and_retrieve_account(db_session: Session):
    """Test basic CRUD operations for Account model"""
    from src.models import Account
    
    # Create
    account = Account(
        id="test_db_acc_123",
        name="Test DB Account",
        type="checking",
        currency="USD",
        balance=1000.00,
        org_name="Test Bank",
        url="https://test-bank.com",
        last_updated=datetime.now(timezone.utc)
    )
    db_session.add(account)
    db_session.commit()
    
    # Retrieve
    db_account = db_session.query(Account).filter_by(id="test_db_acc_123").first()
    assert db_account is not None
    assert db_account.name == "Test DB Account"
    assert db_account.type == "checking"
    
    # Cleanup
    db_session.delete(db_account)
    db_session.commit()

def test_can_create_transaction_with_relationship(db_session: Session, test_account_data):
    """Test creating a transaction with account relationship"""
    from src.models import Account, Transaction
    
    # Create account first
    account = Account(**test_account_data)
    db_session.add(account)
    
    # Create transaction
    transaction = Transaction(
        id="test_txn_456",
        account_id=test_account_data["id"],
        posted_date=datetime.now(timezone.utc),
        amount=100.00,
        description="Test Transaction"
    )
    db_session.add(transaction)
    db_session.commit()
    
    # Verify relationship
    db_transaction = db_session.query(Transaction).filter_by(id="test_txn_456").first()
    assert db_transaction is not None
    assert db_transaction.account_id == test_account_data["id"]
    assert db_transaction.amount == 100.00
    
    # Cleanup
    db_session.delete(db_transaction)
    db_session.delete(account)
    db_session.commit()

def test_budget_category_relationship(db_session: Session, test_account_data):
    """Test relationship between transactions and budget categories"""
    from src.models import Account, BudgetCategory, Transaction
    
    # Create account
    account = Account(**test_account_data)
    db_session.add(account)
    
    # Create budget category
    category = BudgetCategory(name="Groceries", monthly_limit=500.00)
    db_session.add(category)
    db_session.commit()
    
    # Create transaction with category
    transaction = Transaction(
        id="test_txn_789",
        account_id=test_account_data["id"],
        posted_date=datetime.now(timezone.utc),
        amount=75.50,
        description="Grocery Shopping",
        category_id=category.id
    )
    db_session.add(transaction)
    db_session.commit()
    
    # Verify relationship
    db_transaction = db_session.query(Transaction).filter_by(id="test_txn_789").first()
    assert db_transaction is not None
    assert db_transaction.category_id == category.id
    assert db_transaction.category.name == "Groceries"
    
    # Cleanup
    db_session.delete(db_transaction)
    db_session.delete(category)
    db_session.delete(account)
    db_session.commit()

def test_database_transaction_rollback(db_session: Session):
    """Test that database transactions are properly isolated and rolled back"""
    from src.models import Account
    
    # Start a transaction
    account = Account(
        id="temp_acc_rollback",
        name="Temporary Account for Rollback",
        type="checking",
        currency="USD",
        balance=1000.00,
        last_updated=datetime.now(timezone.utc)
    )
    db_session.add(account)
    
    # Verify the account exists in this session
    assert db_session.query(Account).filter_by(id="temp_acc_rollback").first() is not None
    
    # Rollback the transaction
    db_session.rollback()
    
    # Verify the account was not committed
    assert db_session.query(Account).filter_by(id="temp_acc_rollback").first() is None
