from pydantic import BaseModel, Field, ConfigDict
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
    currency: Optional[str] = 'USD'
    balance: Optional[float] = None
    org_name: Optional[str] = None
    url: Optional[str] = None

class TransactionBase(BaseModel):
    account_id: str
    posted_date: datetime
    description: Optional[str] = None
    amount: float
    memo: Optional[str] = None
    payee: Optional[str] = None
    pending: Optional[bool] = False
    category: Optional[str] = Field(None, max_length=32)

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
    balance: Optional[float] = None
    org_name: Optional[str] = None
    url: Optional[str] = None

class TransactionUpdate(TransactionBase):
    account_id: Optional[str] = None
    posted_date: Optional[datetime] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    memo: Optional[str] = None
    payee: Optional[str] = None
    pending: Optional[bool] = None
    category: Optional[str] = Field(None, max_length=32)

# Response schemas
class Account(AccountBase):
    id: str
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        json_schema_extra={
            "exclude": ["transaction_metadata"]
        }
    )

class Transaction(TransactionBase):
    id: str
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

# Budget and Savings schemas
class BudgetCategoryBase(BaseModel):
    name: str
    monthly_limit: float = 0.0

class BudgetCategoryCreate(BudgetCategoryBase):
    pass

class BudgetCategoryUpdate(BaseModel):
    name: Optional[str] = None
    monthly_limit: Optional[float] = None

class BudgetCategory(BudgetCategoryBase):
    id: int
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

class SavingsBucketBase(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0.0
    goal_date: Optional[date] = None

class SavingsBucketCreate(SavingsBucketBase):
    pass

class SavingsBucketUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    goal_date: Optional[date] = None

class SavingsBucket(SavingsBucketBase):
    id: int
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None
        }
    )
