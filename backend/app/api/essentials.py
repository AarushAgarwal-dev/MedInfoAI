from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Medicine

router = APIRouter(prefix="/essentials", tags=["essentials"])

ESSENTIALS = {
    "pain": ["Paracetamol", "Ibuprofen"],
    "cold": ["Cetirizine", "Paracetamol"],
    "fever": ["Paracetamol", "Ibuprofen"],
}

@router.get("/")
def get_essentials():
    return {"categories": list(ESSENTIALS.keys())}

@router.get("/{category}")
def get_by_category(category: str, db: Session = Depends(get_db)):
    names = ESSENTIALS.get(category, [])
    medicines = db.query(Medicine).filter(Medicine.name.in_(names)).all()
    return {"medicines": [{"id": m.id, "name": m.name, "generic": m.generic, "company": m.company, "price": m.price} for m in medicines]} 