import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import IntegrityError

from src import models

def test_create_account():
    """Test creating an account with valid data"""
    account = models.Account(
        id="test_acc_123",
        name="Test Account",
        type="checking",
        currency="USD",
        balance=1000.00,
        org_name="Test Bank",
        url="https://test-bank.com"
    )

    assert account is not None
    assert account.name == "Test Account"
    assert account.type == "checking"
    assert account.balance == 1000.00
    assert account.org_name == "Test Bank"
    assert account.currency == "USD"
    assert account.url == "https://test-bank.com"

def test_create_transaction():
    """Test creating a transaction with valid data"""
    transaction = models.Transaction(
        id="test_txn_123",
        account_id="test_acc_123",
        amount=100.00,
        description="Test Transaction",
        payee="Test Payee",
        posted_date=datetime.now(timezone.utc)
    )

    assert transaction is not None
    assert transaction.id == "test_txn_123"
    assert transaction.account_id == "test_acc_123"
    assert transaction.amount == 100.00
    assert transaction.description == "Test Transaction"
    assert transaction.payee == "Test Payee"
    assert transaction.posted_date is not None

def test_budget_category_creation():
    """Test creating a budget category"""
    category = models.BudgetCategory(
        id=1,
        name="Groceries",
        monthly_limit=500.00
    )
    
    assert category is not None
    assert category.name == "Groceries"
    assert category.monthly_limit == 500.00

def test_savings_bucket_creation():
    """Test creating a savings bucket"""
    bucket = models.SavingsBucket(
        id=1,
        name="Vacation",
        target_amount=5000.00,
        current_amount=1000.00,
        goal_date=datetime.now(timezone.utc).date() + timedelta(days=365)
    )
    
    assert bucket is not None
    assert bucket.name == "Vacation"
    assert bucket.target_amount == 5000.00
    assert bucket.current_amount == 1000.00
    assert bucket.goal_date is not None
