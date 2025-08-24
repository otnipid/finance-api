from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class AccountBase(BaseModel):
    name: str
    type: Optional[str]
    institution: Optional[str]
    account_number_last4: Optional[str]
    currency: Optional[str] = 'USD'
    current_balance: Optional[float] = 0.00

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    id: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    account_id: int
    date: date
    description: Optional[str]
    category: Optional[str]
    amount: float

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class BudgetCategoryBase(BaseModel):
    name: str
    monthly_limit: Optional[float] = 0.0

class BudgetCategoryCreate(BudgetCategoryBase):
    pass

class BudgetCategory(BudgetCategoryBase):
    id: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class SavingsBucketBase(BaseModel):
    name: str
    target_amount: float
    current_amount: Optional[float] = 0.0
    goal_date: Optional[date]

class SavingsBucketCreate(SavingsBucketBase):
    pass

class SavingsBucket(SavingsBucketBase):
    id: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True
