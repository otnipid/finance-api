from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Text, TIMESTAMP
from database import Base

class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50))
    institution = Column(String(100))
    account_number_last4 = Column(String(4))
    currency = Column(String(3), default='USD')
    current_balance = Column(Numeric(12, 2), default=0.00)
    created_at = Column(TIMESTAMP)

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id', ondelete='CASCADE'))
    date = Column(Date, nullable=False)
    description = Column(Text)
    category = Column(String(100))
    amount = Column(Numeric(12, 2), nullable=False)
    created_at = Column(TIMESTAMP)

class BudgetCategory(Base):
    __tablename__ = 'budget_categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    monthly_limit = Column(Numeric(12, 2), default=0.00)
    created_at = Column(TIMESTAMP)

class SavingsBucket(Base):
    __tablename__ = 'savings_buckets'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    target_amount = Column(Numeric(12, 2), nullable=False)
    current_amount = Column(Numeric(12, 2), default=0.00)
    goal_date = Column(Date)
    created_at = Column(TIMESTAMP)