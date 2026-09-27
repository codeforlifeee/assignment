from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter(prefix="/centres", tags=["centres"])

@router.get("/", response_model=List[schemas.CentreResponse])
def get_centres(db: Session = Depends(database.get_db), skip: int = 0, limit: int = 100):
    return db.query(models.Centre).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.CentreResponse, status_code=201)
def create_centre(centre: schemas.CentreCreate, db: Session = Depends(database.get_db)):
    new_centre = models.Centre(**centre.model_dump())
    db.add(new_centre)
    db.commit()
    db.refresh(new_centre)
    return new_centre

@router.post("/{centre_id}/tests", response_model=schemas.DiagnosticTestResponse, status_code=201)
def add_test_to_centre(centre_id: int, test: schemas.DiagnosticTestCreate, db: Session = Depends(database.get_db)):
    db_centre = db.query(models.Centre).filter(models.Centre.id == centre_id).first()
    if not db_centre:
        raise HTTPException(status_code=404, detail="Centre not found")
    
    new_test = models.DiagnosticTest(**test.model_dump(), centre_id=centre_id)
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    return new_test
