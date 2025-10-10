from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum

# Enums
class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    LOAN = "loan"
    INVESTMENT = "investment"
    OTHER = "other"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    POSTED = "posted"
    CANCELLED = "cancelled"

# Base schemas
class AccountBase(BaseModel):
    name: str
    type: Optional[AccountType] = None
    institution: Optional[str] = None
    number: Optional[str] = None
    currency: Optional[str] = 'USD'
    org_name: Optional[str] = None
    url: Optional[str] = None
    username: Optional[str] = None
    last_updated: Optional[datetime] = None

class TransactionBase(BaseModel):
    account_id: str
    date: datetime
    description: Optional[str] = None
    amount: float
    memo: Optional[str] = None
    payee: Optional[str] = None
    pending: Optional[bool] = False
    metadata: Optional[Dict[str, Any]] = None

# Create schemas
class AccountCreate(AccountBase):
    id: str  # SimpleFin account ID

class TransactionCreate(TransactionBase):
    id: str  # SimpleFin transaction ID

# Update schemas
class AccountUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[AccountType] = None
    currency: Optional[str] = None
    institution: Optional[str] = None
    number: Optional[str] = None
    org_name: Optional[str] = None
    url: Optional[str] = None
    username: Optional[str] = None
    last_updated: Optional[datetime] = None

class TransactionUpdate(TransactionBase):
    account_id: Optional[str] = None
    date: Optional[datetime] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    memo: Optional[str] = None
    payee: Optional[str] = None
    pending: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

# Response schemas
class Account(AccountBase):
    id: str
    last_updated: Optional[datetime] = None

    class Config:
        orm_mode = True
        fields = {
            'transaction_metadata': {'exclude': True}
        }

class Transaction(TransactionBase):
    id: str
    transaction_metadata: Optional[Dict[str, Any]] = Field(alias="metadata")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

# Budget and Savings schemas
class BudgetCategoryBase(BaseModel):
    name: str
    monthly_limit: float = 0.0

class BudgetCategoryCreate(BudgetCategoryBase):
    pass

class BudgetCategory(BudgetCategoryBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class SavingsBucketBase(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0.0
    goal_date: Optional[date] = None

class SavingsBucketCreate(SavingsBucketBase):
    pass

class SavingsBucket(SavingsBucketBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
