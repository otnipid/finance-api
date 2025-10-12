import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

from src.models import Account, Transaction, BudgetCategory, SavingsBucket

def test_create_account(db_session):
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
    db_session.add(account)
    db_session.commit()
    
    # Verify the account was created with correct data
    db_account = db_session.query(Account).filter(Account.id == "test_acc_123").first()
    assert db_account is not None
    assert db_account.name == "Test Account"
    assert db_account.type == "checking"
    assert db_account.balance == 1000.00

def test_create_transaction(db_session, test_account_data):
    """Test creating a transaction with valid data"""
    # First create an account
    account = Account(**test_account_data)
    db_session.add(account)
    db_session.commit()
    
    # Create a transaction
    transaction = Transaction(
        id="test_txn_123",
        account_id="test_account_123",
        posted_date=datetime(2023, 10, 12, 12, 0, 0, tzinfo=timezone.utc),
        amount=100.00,
        description="Test Transaction",
        memo="Test memo",
        payee="Test Payee",
        pending=False
    )
    db_session.add(transaction)
    db_session.commit()
    
    # Verify the transaction was created with correct data
    db_transaction = db_session.query(Transaction).filter(Transaction.id == "test_txn_123").first()
    assert db_transaction is not None
    assert db_transaction.amount == 100.00
    assert db_transaction.description == "Test Transaction"
    assert db_transaction.account_id == "test_account_123"

def test_transaction_relationships(db_session, test_account_data):
    """Test the relationship between Account and Transaction"""
    # Create an account with transactions
    account = Account(**test_account_data)
    transaction1 = Transaction(
        id="txn1",
        account_id="test_account_123",
        posted_date=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
        amount=100.00,
        description="Transaction 1"
    )
    transaction2 = Transaction(
        id="txn2",
        account_id="test_account_123",
        posted_date=datetime(2023, 10, 2, 12, 0, 0, tzinfo=timezone.utc),
        amount=200.00,
        description="Transaction 2"
    )
    
    account.transactions.extend([transaction1, transaction2])
    db_session.add(account)
    db_session.commit()
    
    # Verify the relationships
    db_account = db_session.query(Account).filter(Account.id == "test_account_123").first()
    assert len(db_account.transactions) == 2
    assert db_account.transactions[0].id == "txn1"
    assert db_account.transactions[1].id == "txn2"
    assert db_account.transactions[0].account == db_account

def test_budget_category_creation(db_session):
    """Test creating a budget category"""
    category = BudgetCategory(
        name="Groceries",
        monthly_limit=500.00
    )
    db_session.add(category)
    db_session.commit()
    
    db_category = db_session.query(BudgetCategory).filter(BudgetCategory.name == "Groceries").first()
    assert db_category is not None
    assert db_category.monthly_limit == 500.00

def test_savings_bucket_creation(db_session):
    """Test creating a savings bucket"""
    savings = SavingsBucket(
        name="Emergency Fund",
        target_amount=10000.00,
        current_amount=2500.00,
        goal_date=datetime(2024, 12, 31, tzinfo=timezone.utc).date()
    )
    db_session.add(savings)
    db_session.commit()
    
    db_savings = db_session.query(SavingsBucket).filter(SavingsBucket.name == "Emergency Fund").first()
    assert db_savings is not None
    assert db_savings.target_amount == 10000.00
    assert db_savings.current_amount == 2500.00
    assert db_savings.goal_date.year == 2024
