from datetime import datetime, timezone
from src.database import Base
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Text, TIMESTAMP, JSON, Boolean, func
from sqlalchemy.orm import relationship

class Account(Base):
    __tablename__ = 'accounts'

    id = Column(String, primary_key=True, index=True)  # SimpleFin account ID
    name = Column(Text, nullable=False)
    currency = Column(Text)
    type = Column(Text)
    balance = Column(Numeric(15, 2))  # Current account balance
    org_name = Column(Text)  # Organization name (e.g., Fidelity, Chase)
    url = Column(Text)  # Institution URL
    last_updated = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(String, primary_key=True, index=True)  # SimpleFin transaction ID
    account_id = Column(String, ForeignKey('accounts.id', ondelete='CASCADE'))
    category_id = Column(Integer, ForeignKey('budget_categories.id', ondelete='SET NULL'), nullable=True)
    posted_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(Text)
    memo = Column(Text)
    payee = Column(Text)
    pending = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    account = relationship("Account", back_populates="transactions")
    category = relationship("BudgetCategory", back_populates="transactions")

class BudgetCategory(Base):
    __tablename__ = 'budget_categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    monthly_limit = Column(Numeric(12, 2), default=0.00)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    transactions = relationship("Transaction", back_populates="category")

class SavingsBucket(Base):
    __tablename__ = 'savings_buckets'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    target_amount = Column(Numeric(12, 2), nullable=False)
    current_amount = Column(Numeric(12, 2), default=0.00)
    goal_date = Column(Date)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())