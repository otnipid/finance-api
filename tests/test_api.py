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
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == TEST_ACCOUNT["id"]
    assert data["name"] == TEST_ACCOUNT["name"]
    assert data["type"] == TEST_ACCOUNT["type"]
    assert data["balance"] == TEST_ACCOUNT["balance"]

def test_get_account(client: TestClient, db: Session):
    """Test retrieving an account"""
    # Create an account first
    account = models.Account(**TEST_ACCOUNT)
    db.add(account)
    db.commit()
    
    # Retrieve the account
    response = client.get(f"/api/accounts/{TEST_ACCOUNT['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == TEST_ACCOUNT["id"]
    assert data["name"] == TEST_ACCOUNT["name"]

def test_update_account(client: TestClient, db: Session):
    """Test updating an account"""
    # Create an account first
    account = models.Account(**TEST_ACCOUNT)
    db.add(account)
    db.commit()
    
    # Update the account
    update_data = {"name": "Updated Account Name", "balance": 2000.00}
    response = client.put(
        f"/api/accounts/{TEST_ACCOUNT['id']}",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Account Name"
    assert data["balance"] == 2000.00

def test_delete_account(client: TestClient, db: Session):
    """Test deleting an account"""
    # Create an account first
    account = models.Account(**TEST_ACCOUNT)
    db.add(account)
    db.commit()
    
    # Delete the account
    response = client.delete(f"/api/accounts/{TEST_ACCOUNT['id']}")
    assert response.status_code == 204
    
    # Verify it's gone
    response = client.get(f"/api/accounts/{TEST_ACCOUNT['id']}")
    assert response.status_code == 404

def test_create_transaction(client: TestClient, db: Session):
    """Test creating a transaction"""
    # Create an account first
    account = models.Account(**TEST_ACCOUNT)
    db.add(account)
    db.commit()
    
    # Create transaction
    transaction_data = {
        "id": "test_txn_123",
        "account_id": TEST_ACCOUNT["id"],
        "posted_date": "2023-10-12T12:00:00Z",
        "amount": 100.00,
        "description": "Test Transaction",
        "memo": "Test memo",
        "payee": "Test Payee",
        "pending": False
    }
    
    response = client.post("/api/transactions/", json=transaction_data)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "test_txn_123"
    assert data["amount"] == 100.00
    assert data["account_id"] == TEST_ACCOUNT["id"]

def test_get_transactions_with_filters(client: TestClient, db: Session):
    """Test getting transactions with filters"""
    # Create test data
    account = models.Account(**TEST_ACCOUNT)
    db.add(account)
    
    # Create transactions with different dates
    for i in range(1, 6):
        transaction = models.Transaction(
            id=f"txn{i}",
            account_id=TEST_ACCOUNT["id"],
            posted_date=datetime(2023, 10, i, 12, 0, 0, tzinfo=timezone.utc),
            amount=float(i * 10),
            description=f"Transaction {i}"
        )
        db.add(transaction)
    
    db.commit()
    
    # Test date range filter
    params = {
        "start_date": "2023-10-02T00:00:00Z",
        "end_date": "2023-10-04T23:59:59Z"
    }
    response = client.get("/api/transactions/", params=params)
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 3  # Should include txn2, txn3, txn4
    
    # Verify ordering (most recent first)
    assert transactions[0]["id"] == "txn4"
    assert transactions[-1]["id"] == "txn2"

def test_health_check(client: TestClient):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# Budget Category Tests
def test_budget_category_crud(client: TestClient, db: Session):
    """Test all budget category CRUD operations"""
    # Create
    category_data = {"name": "Groceries", "monthly_limit": 500.00}
    response = client.post("/api/budget-categories/", json=category_data)
    assert response.status_code == 201
    category = response.json()
    assert category["name"] == "Groceries"
    
    # Read all
    response = client.get("/api/budget-categories/")
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) == 1
    assert categories[0]["name"] == "Groceries"
    
    # Update
    update_data = {"name": "Groceries", "monthly_limit": 600.00}
    response = client.put(f"/api/budget-categories/{category['id']}", json=update_data)
    assert response.status_code == 200
    assert response.json()["monthly_limit"] == 600.00
    
    # Delete
    response = client.delete(f"/api/budget-categories/{category['id']}")
    assert response.status_code == 204
    
    # Verify it's gone
    response = client.get(f"/api/budget-categories/{category['id']}")
    assert response.status_code == 404

# Savings Bucket Tests
def test_savings_bucket_crud(client: TestClient, db: Session):
    """Test all savings bucket CRUD operations"""
    # Create
    bucket_data = {
        "name": "Emergency Fund",
        "target_amount": 10000.00,
        "current_amount": 1000.00,
        "goal_date": "2024-12-31"
    }
    response = client.post("/api/savings-buckets/", json=bucket_data)
    assert response.status_code == 201
    bucket = response.json()
    assert bucket["name"] == "Emergency Fund"
    
    # Read all
    response = client.get("/api/savings-buckets/")
    assert response.status_code == 200
    buckets = response.json()
    assert len(buckets) == 1
    assert buckets[0]["target_amount"] == 10000.00
    
    # Update
    update_data = {
        "name": "Emergency Fund",
        "target_amount": 15000.00,
        "current_amount": 1000.00,
        "goal_date": "2024-12-31"
    }
    response = client.put(f"/api/savings-buckets/{bucket['id']}", json=update_data)
    assert response.status_code == 200
    assert response.json()["target_amount"] == 15000.00
    
    # Delete
    response = client.delete(f"/api/savings-buckets/{bucket['id']}")
    assert response.status_code == 204
    
    # Verify it's gone
    response = client.get(f"/api/savings-buckets/{bucket['id']}")
    assert response.status_code == 404
