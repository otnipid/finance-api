import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text

from src import models

@pytest.mark.integration
def test_create_account(client, db: Session):
    # Clean up any existing test data
    db.execute(text("DELETE FROM transactions WHERE account_id = 'test_acc_456'"))
    db.execute(text("DELETE FROM accounts WHERE id = 'test_acc_456'"))
    db.commit()
    
    account_data = {
        "id": "test_acc_456",
        "name": "New Test Account",
        "type": "savings",
        "balance": 500.00,
        "org_name": "Test Bank",
        "currency": "USD"
    }
    
    # Test creating the account
    response = client.post("/api/accounts/", json=account_data)
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert data["name"] == "New Test Account"
    assert data["type"] == "savings"
    assert data["id"] == "test_acc_456"
    
    # Refresh the session to ensure we have the latest data
    db.expire_all()
    
    # Verify the account exists in the database
    db_account = db.query(models.Account).filter(models.Account.id == "test_acc_456").first()
    assert db_account is not None, "Account was not created in the database"
    assert db_account.name == "New Test Account"
    assert db_account.type == "savings"
    assert float(db_account.balance) == 500.00

@pytest.mark.integration
def test_get_account(client, db: Session):
    # Create a test account directly in the database
    test_account = models.Account(
        id="test_get_account_123",
        name="Test Get Account",
        type="checking",
        balance=1000.00,
        org_name="Test Bank"
    )
    db.add(test_account)
    db.commit()
    
    # Get the account ID
    account_id = test_account.id
    
    # Make the API request
    response = client.get(f"/api/accounts/{account_id}")
    assert response.status_code == 200, f"Failed to get account: {response.text}"
    
    # Verify the response
    data = response.json()
    assert data["id"] == account_id
    assert data["name"] == "Test Get Account"

@pytest.mark.integration
def test_create_transaction(client, db: Session):
    # Create a test account first
    test_account = models.Account(
        id="test_transaction_account",
        name="Test Transaction Account",
        type="checking",
        balance=1000.00,
        org_name="Test Bank"
    )
    db.add(test_account)
    db.commit()
    
    # Clean up any existing test transactions
    db.execute(text("DELETE FROM transactions WHERE id = 'test_txn_123'"))
    db.commit()
    
    transaction_data = {
        "id": "test_txn_123",
        "account_id": test_account.id,
        "amount": 100.00,
        "description": "Test Transaction",
        "posted_date": datetime.now(timezone.utc).isoformat()
    }
    
    # Test creating the transaction
    response = client.post("/api/transactions/", json=transaction_data)
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}. Response: {response.text}"
    
    # Verify the response
    data = response.json()
    assert data["id"] == "test_txn_123"
    assert data["account_id"] == test_account.id
    assert data["amount"] == 100.00
    
    # Refresh the session to ensure we have the latest data
    db.expire_all()
    
    # Verify the transaction exists in the database
    db_transaction = db.query(models.Transaction).filter(
        models.Transaction.id == "test_txn_123"
    ).first()
    assert db_transaction is not None, "Transaction was not created in the database"
    assert db_transaction.account_id == test_account.id
    assert float(db_transaction.amount) == 100.00
