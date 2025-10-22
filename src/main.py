from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import os
from pytz import utc
from contextlib import asynccontextmanager
from src.routers import sync

# Import database and models first to ensure tables are registered with SQLAlchemy
from src import models, schemas, crud
from src.database import SessionLocal, engine, init_db, get_db as get_db_dep

# Lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create database tables
    init_db()
    
    yield
    
    # Shutdown: close database connections, etc.
    # No need to close database connections here, as they are handled by get_db dependency

# Create FastAPI app with lifespan
app = FastAPI(
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers after app creation to avoid circular imports
from src.routers import accounts, transactions, budgets, savings_buckets

# Include routers
app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["budgets"])
app.include_router(savings_buckets.router, prefix="/api/savings-buckets", tags=["savings-buckets"])
app.include_router(sync.router, prefix="/api/sync", tags=["sync"])

# Override the default get_db dependency for testing
if os.getenv("TESTING", "").lower() == "true":
    # In testing, we'll override this with the test database session
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
else:
    # In production/development, use the standard get_db
    get_db = get_db_dep

# Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Root endpoint
@app.get("/")
def root():
    return {"message": "Finance API is running"}

# Health Check Endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Only run the app directly if this file is executed (not imported)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)