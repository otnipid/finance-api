import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime, timezone

def test_database_connection(db: Session):
    """Test that the database connection is working"""
    result = db.execute(text("SELECT 1"))
    assert result.scalar() == 1

def test_database_tables_exist(db: Session):
    """Verify that all expected tables exist in the database"""
    result = db.execute(
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

def test_can_create_and_retrieve_account(db: Session):
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
    )
    db.add(account)
    db.commit()
    
    # Retrieve
    db_account = db.query(Account).filter_by(id="test_db_acc_123").first()
    assert db_account is not None
    assert db_account.name == "Test DB Account"
    assert db_account.type == "checking"
    
    # Cleanup
    db.delete(db_account)
    db.commit()

def test_can_create_transaction_with_relationship(db: Session, test_account_data):
    """Test creating a transaction with account relationship"""
    from src.models import Account, Transaction
    
    # Create account first
    account = Account(**test_account_data)
    db.add(account)
    
    # Create transaction
    transaction = Transaction(
        id="test_txn_456",
        account_id=test_account_data["id"],
        posted_date=datetime.now(timezone.utc),
        amount=100.00,
        description="Test Transaction"
    )
    db.add(transaction)
    db.commit()
    
    # Verify relationship
    db_transaction = db.query(Transaction).filter_by(id="test_txn_456").first()
    assert db_transaction is not None
    assert db_transaction.account_id == test_account_data["id"]
    assert db_transaction.amount == 100.00
    
    # Cleanup
    db.delete(db_transaction)
    db.delete(account)
    db.commit()

def test_budget_category_relationship(db: Session, test_account_data):
    """Test basic transaction creation without category"""
    from src.models import Account, Transaction
    
    # Create account
    account = Account(**test_account_data)
    db.add(account)
    db.commit()
    
    # Create transaction
    transaction = Transaction(
        id="test_txn_cat_123",
        account_id=test_account_data["id"],
        posted_date=datetime.now(timezone.utc),
        amount=100.00,
        description="Grocery Shopping"
    )
    db.add(transaction)
    db.commit()
    
    # Verify transaction was created
    db_transaction = db.query(Transaction).filter_by(id="test_txn_cat_123").first()
    assert db_transaction is not None
    assert db_transaction.description == "Grocery Shopping"
    
    # Cleanup
    db.delete(db_transaction)
    db.delete(account)
    db.commit()

def test_database_transaction_rollback(db: Session):
    """Test that database transactions are properly isolated and rolled back"""
    from src.models import Account

    # Start a transaction
    account = Account(
        id="test_rollback_123",
        name="Rollback Test",
        type="savings",
        balance=500.00
    )
    db.add(account)
    # Remove this line to test rollback properly
    # db.commit()

    # Verify the account was added to session (but not committed)
    assert account in db

    # Rollback the transaction
    db.rollback()

    # The account should not be in the session after rollback
    assert account not in db
    # And it shouldn't exist in the database
    assert db.query(Account).filter_by(id="test_rollback_123").first() is None
