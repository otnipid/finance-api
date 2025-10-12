import pytest
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone

from src import models

@pytest.mark.integration
def test_database_connection(db: Session):
    """Test database connection and table creation"""
    # This test will fail if the database connection fails
    result = db.execute(text("SELECT 1"))
    assert result.scalar() == 1

@pytest.mark.integration
def test_can_create_and_retrieve_account(db: Session):
    """Test creating and retrieving an account from the database"""
    # Create test account
    account = models.Account(
        id="test_acc_123",
        name="Test Account",
        type="checking",
        balance=1000.00,
        org_name="Test Bank"
    )
    db.add(account)
    db.commit()
    
    # Retrieve the account
    db_account = db.query(models.Account).filter(models.Account.id == "test_acc_123").first()
    
    # Verify the account was saved and retrieved correctly
    assert db_account is not None
    assert db_account.name == "Test Account"
    assert db_account.type == "checking"
    assert db_account.balance == 1000.00
    assert db_account.org_name == "Test Bank"

@pytest.mark.integration
def test_can_create_transaction_with_relationship(db: Session):
    """Test creating a transaction with a relationship to an account"""
    # Create test account
    account = models.Account(
        id="test_acc_123",
        name="Test Account",
        type="checking",
        balance=1000.00,
        org_name="Test Bank"
    )
    db.add(account)
    db.commit()

    # Create transaction for the account
    posted_date = datetime.now(timezone.utc).replace(microsecond=0)
    transaction = models.Transaction(
        id="test_txn_123",
        account_id=account.id,
        amount=100.00,
        description="Test Transaction",
        payee="Test Payee",
        posted_date=posted_date
    )
    db.add(transaction)
    db.commit()

    # Verify the transaction was saved with the correct relationship
    db_transaction = db.query(models.Transaction).filter(
        models.Transaction.id == "test_txn_123"
    ).first()

    assert db_transaction is not None
    assert db_transaction.account_id == account.id
    assert db_transaction.amount == 100.00
    # Compare timestamps by removing timezone info and microseconds
    assert db_transaction.posted_date.replace(tzinfo=None) == posted_date.replace(tzinfo=None)
    
    # Verify the relationship works
    assert db_transaction.account is not None
    assert db_transaction.account.id == account.id
