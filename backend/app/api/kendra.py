from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Kendra
from pydantic import BaseModel

router = APIRouter(prefix="/kendra", tags=["kendra"])

@router.get("/nearby")
def find_nearest(lat: float = Query(...), lng: float = Query(...), db: Session = Depends(get_db)):
    # For now, return all Kendras (can add geospatial filtering later)
    kendras = db.query(Kendra).all()
    return {"kendras": [{"id": k.id, "name": k.name, "lat": k.lat, "lng": k.lng} for k in kendras]}

class KendraIn(BaseModel):
    name: str
    lat: float
    lng: float

@router.post("/")
def create_kendra(k: KendraIn, db: Session = Depends(get_db)):
    db_k = Kendra(name=k.name, lat=k.lat, lng=k.lng)
    db.add(db_k)
    db.commit()
    db.refresh(db_k)
    return {"id": db_k.id, "name": db_k.name} 