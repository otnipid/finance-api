import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import models first to ensure all tables are registered with SQLAlchemy
from src import models
from src.database import Base
from src.main import app, get_db

# Create a test SQLite database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
@pytest.fixture(scope="function")
def db_session():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new database session
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Begin a nested transaction
    nested = connection.begin_nested()
    
    # If the application code calls session.commit, it will end the nested
    # transaction. We need to start a new one when that happens.
    @event.listens_for(session, 'after_transaction_end')
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.expire_all()
            session.begin_nested()

    yield session

    # Cleanup after test
    session.close()
    transaction.rollback()
    connection.close()
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)

# Fixture to override the database dependency in FastAPI app
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.rollback()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides = {}

# Fixture for test data
@pytest.fixture
def test_account_data():
    return {
        "id": "test_account_123",
        "name": "Test Account",
        "type": "checking",
        "currency": "USD",
        "balance": 1000.00,
        "org_name": "Test Bank",
        "url": "https://test-bank.com",
        "last_updated": "2023-01-01T00:00:00Z"
    }

@pytest.fixture
def test_transaction_data():
    return {
        "id": "test_txn_123",
        "account_id": "test_account_123",
        "posted_date": "2023-10-12T12:00:00Z",
        "amount": 100.00,
        "description": "Test Transaction",
        "memo": "Test memo",
        "payee": "Test Payee",
        "pending": False,
        "category_id": None
    }

@pytest.fixture
def test_budget_category_data():
    return {
        "name": "Test Category",
        "monthly_limit": 1000.00
    }

@pytest.fixture
def test_savings_bucket_data():
    return {
        "name": "Test Savings",
        "target_amount": 5000.00,
        "current_amount": 1000.00,
        "goal_date": "2024-12-31"
    }
