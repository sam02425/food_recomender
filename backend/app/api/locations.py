from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.db import SessionLocal
from app.models.location import Location

router = APIRouter(prefix="/api/locations", tags=["locations"])

# Pydantic Schemas
class LocationOut(BaseModel):
    id: int
    name: str
    address: str
    hours: str
    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[LocationOut])
def list_locations(db: Session = Depends(get_db)):
    return db.query(Location).all()

@router.get("/{location_id}", response_model=LocationOut)
def get_location(location_id: int, db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc
