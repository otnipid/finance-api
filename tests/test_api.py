import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from src.main import app
from src import models, schemas, crud

# Test data
TEST_ACCOUNT = {
    "id": "test_acc_123",
    "name": "Test Account",
    "type": "checking",
    "currency": "USD",
    "balance": 1000.00,
    "org_name": "Test Bank",
    "url": "https://test-bank.com"
}

def test_create_account(client: TestClient):
    """Test creating a new account"""
    response = client.post("/api/accounts/", json=TEST_ACCOUNT)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["id"] == TEST_ACCOUNT["id"]
    assert data["name"] == TEST_ACCOUNT["name"]
    assert data["type"] == TEST_ACCOUNT["type"]
    assert data["balance"] == TEST_ACCOUNT["balance"]

def test_get_account(client: TestClient, db: Session):
    """Test retrieving an account"""
    # Create test account
    db_account = models.Account(**TEST_ACCOUNT)
    db.add(db_account)
    db.commit()
    
    # Test retrieval
    response = client.get(f"/api/accounts/{TEST_ACCOUNT['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == TEST_ACCOUNT["id"]
    assert data["name"] == TEST_ACCOUNT["name"]

def test_update_account(client: TestClient, db: Session):
    """Test updating an account"""
    # Create test account
    db_account = models.Account(**TEST_ACCOUNT)
    db.add(db_account)
    db.commit()
    
    # Test update
    update_data = {"name": "Updated Account Name"}
    response = client.put(
        f"/api/accounts/{TEST_ACCOUNT['id']}",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Account Name"

def test_delete_account(client: TestClient, db: Session):
    """Test deleting an account"""
    # Create test account
    db_account = models.Account(**TEST_ACCOUNT)
    db.add(db_account)
    db.commit()
    
    # Test deletion
    response = client.delete(f"/api/accounts/{TEST_ACCOUNT['id']}")
    assert response.status_code == 204
    
    # Verify it's gone
    response = client.get(f"/api/accounts/{TEST_ACCOUNT['id']}")
    assert response.status_code == 404

def test_create_transaction(client: TestClient, db: Session):
    """Test creating a transaction"""
    # Create test account
    db_account = models.Account(**TEST_ACCOUNT)
    db.add(db_account)
    db.commit()
    
    # Test transaction creation
    transaction_data = {
        "id": "test_txn_123",
        "account_id": TEST_ACCOUNT["id"],
        "posted_date": datetime.now(timezone.utc).isoformat(),
        "amount": 100.00,
        "description": "Test Transaction",
        "memo": "Test memo",
        "payee": "Test Payee",
        "pending": False
    }
    response = client.post("/api/transactions/", json=transaction_data)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["id"] == "test_txn_123"
    assert data["amount"] == 100.00

def test_get_transactions_with_filters(client: TestClient, db: Session):
    """Test getting transactions with filters"""
    # Create test accounts and transactions
    account1 = models.Account(
        id="acc1",
        name="Account 1",
        type="checking"
    )
    account2 = models.Account(
        id="acc2",
        name="Account 2",
        type="savings"
    )
    db.add_all([account1, account2])

    # Create transactions with explicit posted_dates to ensure consistent ordering
    now = datetime.now(timezone.utc)
    txn1 = models.Transaction(
        id="txn1",
        account_id="acc1",
        posted_date=now - timedelta(days=2),
        amount=50.00,
        description="Test Transaction 1"
    )
    txn2 = models.Transaction(
        id="txn2",
        account_id="acc2",
        posted_date=now - timedelta(days=1),
        amount=100.00,
        description="Test Transaction 2"
    )
    db.add_all([txn1, txn2])
    db.commit()

    # Test filtering by account
    response = client.get("/api/transactions/?account_id=acc1")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 1
    assert transactions[0]["id"] == "txn1"

    # Test getting all transactions - they should be ordered by posted_date descending
    response = client.get("/api/transactions/")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 2
    # The most recent transaction should be first
    assert transactions[0]["id"] == "txn2"  # More recent
    assert transactions[1]["id"] == "txn1"  # Older

def test_health_check(client: TestClient):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "timestamp" in data
    # Verify the timestamp is in ISO format
    try:
        datetime.fromisoformat(data["timestamp"])
    except ValueError:
        pytest.fail("Timestamp is not in ISO format")

# Budget Category Tests
def test_budget_category_crud(client: TestClient, db: Session):
    """Test all budget category CRUD operations"""
    # Create
    category_data = {"name": "Groceries", "monthly_limit": 500.00}
    response = client.post("/api/budgets/", json=category_data)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    category = response.json()
    assert category["name"] == "Groceries"
    
    # Read all
    response = client.get("/api/budgets/")
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) == 1
    assert categories[0]["name"] == "Groceries"
    
    # Update
    update_data = {"name": "Groceries", "monthly_limit": 600.00}
    response = client.put(f"/api/budgets/{category['id']}", json=update_data)
    assert response.status_code == 200
    assert response.json()["monthly_limit"] == 600.00
    
    # Delete
    response = client.delete(f"/api/budgets/{category['id']}")
    assert response.status_code == 204
    
    # Verify it's gone
    response = client.get(f"/api/budgets/{category['id']}")
    assert response.status_code == 404

# Savings Bucket Tests
def test_savings_bucket_crud(client: TestClient, db: Session):
    """Test all savings bucket CRUD operations"""
    # Create a test savings bucket
    bucket_data = {
        "name": "Vacation Fund",
        "target_amount": 1000.0,
        "current_amount": 100.0,
        "goal_date": "2023-12-31"
    }
    
    # Test create
    response = client.post("/api/savings-buckets/", json=bucket_data)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    bucket = response.json()
    assert bucket["name"] == "Vacation Fund"
    assert "id" in bucket
    
    # Test get all
    response = client.get("/api/savings-buckets/")
    assert response.status_code == 200
    buckets = response.json()
    assert len(buckets) > 0
    assert any(b["name"] == "Vacation Fund" for b in buckets)
    
    # Test update
    update_data = {"name": "Updated Vacation Fund"}
    response = client.put(f"/api/savings-buckets/{bucket['id']}", json=update_data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    updated_bucket = response.json()
    assert updated_bucket["name"] == "Updated Vacation Fund"
    
    # Test delete
    response = client.delete(f"/api/savings-buckets/{bucket['id']}")
    assert response.status_code == 204, f"Expected 204, got {response.status_code}: {response.text}"
    
    # Verify deletion
    response = client.get(f"/api/savings-buckets/{bucket['id']}")
    assert response.status_code == 404
