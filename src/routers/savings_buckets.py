from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, crud
from ..database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.SavingsBucket, status_code=status.HTTP_201_CREATED)
def create_savings_bucket(
    bucket: schemas.SavingsBucketCreate, 
    db: Session = Depends(get_db)
):
    """Create a new savings bucket"""
    return crud.create_savings_bucket(db=db, bucket=bucket)

@router.get("/", response_model=List[schemas.SavingsBucket])
def read_savings_buckets(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all savings buckets with pagination"""
    return crud.get_savings_buckets(db=db, skip=skip, limit=limit)

@router.get("/{bucket_id}", response_model=schemas.SavingsBucket)
def read_savings_bucket(bucket_id: str, db: Session = Depends(get_db)):
    """Get a specific savings bucket by ID"""
    db_bucket = crud.get_savings_bucket(db, bucket_id=bucket_id)
    if db_bucket is None:
        raise HTTPException(status_code=404, detail="Savings bucket not found")
    return db_bucket

@router.put("/{bucket_id}", response_model=schemas.SavingsBucket)
def update_savings_bucket(
    bucket_id: str, 
    bucket: schemas.SavingsBucketUpdate, 
    db: Session = Depends(get_db)
):
    """Update a savings bucket"""
    db_bucket = crud.get_savings_bucket(db, bucket_id=bucket_id)
    if db_bucket is None:
        raise HTTPException(status_code=404, detail="Savings bucket not found")
    return crud.update_savings_bucket(
        db=db,
        bucket_id=bucket_id,
        bucket_update=bucket
    )

@router.delete("/{bucket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_savings_bucket(bucket_id: str, db: Session = Depends(get_db)):
    """Delete a savings bucket"""
    db_bucket = crud.get_savings_bucket(db, bucket_id=bucket_id)
    if db_bucket is None:
        raise HTTPException(status_code=404, detail="Savings bucket not found")
    crud.delete_savings_bucket(db=db, bucket_id=bucket_id)
    return None
