import os
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Set TESTING environment variable before importing database modules
os.environ["TESTING"] = "true"

# Create a test database URL
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create engine with in-memory SQLite database
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=True  # Enable SQL echo for debugging
)

# Create test session local class
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import after setting up test database
from src.database import Base, get_db
from src.main import app
from src import models

# Override the get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        # Enable foreign keys for SQLite
        db.execute(text("PRAGMA foreign_keys=ON"))
        db.commit()
        yield db
    finally:
        db.close()

# Create all tables before tests and drop them after
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Set up the database override
    app.dependency_overrides[get_db] = override_get_db
    
    yield  # Testing happens here
    
    # Clean up after all tests
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides = {}
    engine.dispose()

# Create a new database session for each test
@pytest.fixture(scope="function")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    # Begin a nested transaction for savepoints
    nested = connection.begin_nested()
    
    # If the application code calls session.commit, it will end the nested
    # transaction. We need to start a new one when that happens.
    @event.listens_for(session, 'after_transaction_end')
    def restart_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active and not connection.in_nested_transaction():
            nested = connection.begin_nested()
    
    # Enable foreign keys for SQLite
    session.execute(text("PRAGMA foreign_keys=ON"))
    session.commit()
    
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
        transaction.rollback()
        connection.close()

# Test client fixture
@pytest.fixture(scope="function")
def client(db):
    def _get_test_db():
        try:
            yield db
        finally:
            db.rollback()
            
    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as test_client:
        yield test_client
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
        "last_updated": datetime.now(timezone.utc)
    }

@pytest.fixture
def test_account(db, test_account_data):
    account = models.Account(**test_account_data)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

@pytest.fixture
def test_transaction_data(test_account):
    return {
        "id": "test_txn_123",
        "account_id": test_account.id,
        "posted_date": datetime.now(timezone.utc).isoformat(),
        "description": "Test Transaction",
        "amount": 100.0,
        "pending": False
    }

@pytest.fixture
def test_transaction(db, test_transaction_data):
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
    category = models.BudgetCategory(**test_budget_category_data)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@pytest.fixture
def test_savings_bucket_data():
    return {
        "name": "Vacation Fund",
        "target_amount": 5000.0,
        "current_amount": 1000.0,
        "goal_date": (datetime.now(timezone.utc) + timedelta(days=365)).date().isoformat()
    }

@pytest.fixture
def test_savings_bucket(db, test_savings_bucket_data):
    bucket = models.SavingsBucket(**test_savings_bucket_data)
    db.add(bucket)
    db.commit()
    db.refresh(bucket)
    return bucket
