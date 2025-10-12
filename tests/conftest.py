import os
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.main import app
from src import models

# Use SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    """Create database engine and tables for testing."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Enable foreign key support for SQLite
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.commit()
    
    yield engine
    
    # Clean up
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(db_engine):
    """
    Create a new database session for each test with a rollback at the end.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    # Begin a nested transaction (using SAVEPOINT).
    nested = connection.begin_nested()
    
    # If the application code calls session.commit, it will end the nested
    # transaction. We need to start a new one when that happens.
    @event.listens_for(session, 'after_transaction_end')
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()
    
    yield session
    
    # Cleanup
    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    """
    Create a test client that uses the `db` fixture for database access.
    """
    def override_get_db():
        try:
            yield db
        finally:
            db.rollback()
    
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear overrides after the test
    app.dependency_overrides = {}

# Test data fixtures
@pytest.fixture
def test_account_data():
    return {
        "id": "test_account_123",
        "name": "Test Account",
        "type": "checking",
        "balance": 1000.0,
        "org_name": "Test Bank",
    }

@pytest.fixture
def test_account(db, test_account_data):
    """Create a test account in the database."""
    account = models.Account(**test_account_data)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

@pytest.fixture
def test_transaction_data(test_account):
    return {
        "id": "test_transaction_123",
        "account_id": test_account.id,
        "amount": 100.0,
        "description": "Test Transaction",
        "payee": "Test Payee",
        "pending": False,
        "posted_date": datetime.now(timezone.utc).isoformat()
    }

@pytest.fixture
def test_transaction(db, test_transaction_data):
    """Create a test transaction in the database."""
    transaction = models.Transaction(**test_transaction_data)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@pytest.fixture
def test_budget_category_data():
    return {
        "name": "Groceries",
        "monthly_limit": 500.0
    }

@pytest.fixture
def test_budget_category(db, test_budget_category_data):
    """Create a test budget category in the database."""
    category = models.BudgetCategory(**test_budget_category_data)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@pytest.fixture
def test_savings_bucket_data():
    return {
        "name": "Vacation",
        "target_amount": 2000.0,
        "current_amount": 500.0,
        "goal_date": (datetime.now(timezone.utc).date() + timedelta(days=180)).isoformat()
    }

@pytest.fixture
def test_savings_bucket(db, test_savings_bucket_data):
    """Create a test savings bucket in the database."""
    bucket = models.SavingsBucket(**test_savings_bucket_data)
    db.add(bucket)
    db.commit()
    db.refresh(bucket)
    return bucket
