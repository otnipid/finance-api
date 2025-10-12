import os
import dotenv
from dotenv import load_dotenv
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Load environment variables from .env file if it exists
env_path = '.env.local' if os.path.exists('.env.local') else '.env'
load_dotenv(env_path)

# Check if we're in test mode
TESTING = os.getenv("TESTING", "false").lower() == "true"

if TESTING:
    # Use SQLite in-memory database for testing
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Enable foreign key support for SQLite in test mode
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if dbapi_connection is not None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
else:
    # Get database URL from environment variables for non-test environments
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URL:
        raise ValueError(
            "DATABASE_URL environment variable is not set. "
            "Please set it in your environment or in a .env file.\n"
            "For local development, you can use: postgresql://user:password@localhost:5432/yourdb\n"
            "For production, make sure to set it in your deployment environment."
        )
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative class definitions
Base = declarative_base()

def get_db() -> Session:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        # Ensure foreign keys are enabled for each new connection in SQLite
        if 'sqlite' in str(engine.url):
            with db.begin():
                db.execute(text("PRAGMA foreign_keys=ON"))
        yield db
    finally:
        db.close()

def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)
    # Ensure foreign keys are enabled after table creation for SQLite
    if 'sqlite' in str(engine.url):
        with SessionLocal() as session:
            session.execute(text("PRAGMA foreign_keys=ON"))
            session.commit()