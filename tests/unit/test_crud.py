import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src import crud, models, schemas

@pytest.fixture
def mock_db():
    # Create a mock database session
    db = MagicMock(spec=Session)
    return db

@pytest.mark.unit
def test_create_account(mock_db):
    """Test creating an account with mock database"""
    # Setup test data
    account_data = schemas.AccountCreate(
        id="test_acc_123",
        name="Test Account",
        type="checking",
        balance=1000.00,
        org_name="Test Bank",
        currency="USD"
    )
    
    # Mock the database add and commit
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    
    # Call the function
    result = crud.create_account(mock_db, account_data)
    
    # Verify the result
    assert result.id == "test_acc_123"
    assert result.name == "Test Account"
    assert result.type == "checking"
    assert result.balance == 1000.00
    assert result.org_name == "Test Bank"
    assert result.currency == "USD"
    
    # Verify the database was called correctly
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.unit
def test_get_account(mock_db):
    """Test getting an account by ID with mock database"""
    # Setup test data
    test_account = models.Account(
        id="test_acc_123",
        name="Test Account",
        type="checking",
        balance=1000.00
    )
    
    # Mock the database query
    mock_db.query.return_value.filter.return_value.first.return_value = test_account
    
    # Call the function
    result = crud.get_account(mock_db, "test_acc_123")
    
    # Verify the result
    assert result.id == "test_acc_123"
    assert result.name == "Test Account"
    
    # Verify the database was queried correctly
    mock_db.query.assert_called_once_with(models.Account)
    mock_db.query.return_value.filter.return_value.first.assert_called_once()

@pytest.mark.unit
def test_create_transaction(mock_db):
    """Test creating a transaction with mock database"""
    # Setup test data
    transaction_data = schemas.TransactionCreate(
        id="test_txn_123",
        account_id="test_acc_123",
        amount=100.00,
        description="Test Transaction",
        posted_date=datetime.now(timezone.utc).isoformat()
    )
    
    # Mock the database add and commit
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    
    # Call the function
    result = crud.create_transaction(mock_db, transaction_data)
    
    # Verify the result
    assert result.id == "test_txn_123"
    assert result.account_id == "test_acc_123"
    assert result.amount == 100.00
    
    # Verify the database was called correctly
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.unit
def test_get_transactions_with_filters(mock_db):
    """Test getting transactions with filters using mock database"""
    # Setup test data
    test_transactions = [
        models.Transaction(
            id="test_txn_123",
            account_id="test_acc_123",
            amount=100.00,
            description="Test Transaction 1",
            posted_date=datetime.now(timezone.utc)
        ),
        models.Transaction(
            id="test_txn_456",
            account_id="test_acc_123",
            amount=200.00,
            description="Test Transaction 2",
            posted_date=datetime.now(timezone.utc)
        )
    ]
    
    # Mock the database query
    mock_query = MagicMock()
    mock_query.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = test_transactions
    mock_db.query.return_value = mock_query
    
    # Call the function
    result = crud.get_transactions(
        db=mock_db,
        account_id="test_acc_123",
        skip=0,
        limit=10
    )
    
    # Verify the result
    assert len(result) == 2
    assert result[0].id == "test_txn_123"
    assert result[1].id == "test_txn_456"
    
    # Verify the database was queried correctly
    mock_db.query.assert_called_once_with(models.Transaction)
    mock_query.filter.assert_called_once()
    mock_query.filter.return_value.order_by.return_value.offset.assert_called_once_with(0)
    mock_query.filter.return_value.order_by.return_value.offset.return_value.limit.assert_called_once_with(10)
