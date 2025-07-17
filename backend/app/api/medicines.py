from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Medicine
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/medicines", tags=["medicines"])

@router.get("/search")
def search_medicines(q: str = Query(..., description="Medicine name to search"), db: Session = Depends(get_db)):
    results = db.query(Medicine).filter(Medicine.name.ilike(f"%{q}%")).all()
    return {"results": [{"id": m.id, "name": m.name, "generic": m.generic, "company": m.company, "price": m.price} for m in results]}

@router.get("/generic")
def get_generic_name(name: str = Query(..., description="Brand or medicine name"), db: Session = Depends(get_db)):
    medicine = db.query(Medicine).filter((Medicine.name.ilike(f"%{name}%")) | (Medicine.generic.ilike(f"%{name}%"))).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    brands = db.query(Medicine).filter(Medicine.generic == medicine.generic).all()
    return {
        "generic": medicine.generic,
        "brands": [{"id": b.id, "name": b.name, "company": b.company, "price": b.price} for b in brands]
    }

class MedicineIn(BaseModel):
    name: str
    generic: str
    company: str
    price: float

@router.post("/")
def create_medicine(med: MedicineIn, db: Session = Depends(get_db)):
    db_med = Medicine(name=med.name, generic=med.generic, company=med.company, price=med.price)
    db.add(db_med)
    db.commit()
    db.refresh(db_med)
    return {"id": db_med.id, "name": db_med.name} 