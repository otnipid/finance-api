from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, crud
from ..database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.BudgetCategory, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget: schemas.BudgetCategoryCreate, 
    db: Session = Depends(get_db)
):
    """Create a new budget category"""
    return crud.create_budget(db=db, budget=budget)

@router.get("/", response_model=List[schemas.BudgetCategory])
def read_budgets(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Read all budget categories"""
    budgets = crud.get_budgets(db, skip=skip, limit=limit)
    return budgets

@router.get("/{budget_id}", response_model=schemas.BudgetCategory)
def read_budget(budget_id: int, db: Session = Depends(get_db)):
    """Get a specific budget category by ID"""
    db_budget = crud.get_budget(db, budget_id=budget_id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget category not found")
    return db_budget

@router.put("/{budget_id}", response_model=schemas.BudgetCategory)
def update_budget(
    budget_id: int, 
    budget: schemas.BudgetCategoryUpdate, 
    db: Session = Depends(get_db)
):
    """Update a budget category"""
    db_budget = crud.get_budget(db, budget_id=budget_id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget category not found")
    return crud.update_budget(db=db, budget_id=budget_id, budget=budget)

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    """Delete a budget category"""
    db_budget = crud.get_budget(db, budget_id=budget_id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget category not found")
    crud.delete_budget(db=db, budget_id=budget_id)
    return None
