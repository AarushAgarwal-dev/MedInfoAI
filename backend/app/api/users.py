from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User, SavedMedicine, Medicine
from passlib.context import CryptContext

router = APIRouter(prefix="/users", tags=["users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class SaveMedicine(BaseModel):
    username: str
    medicine_id: int

@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered successfully"}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}

@router.post("/save")
def save_medicine(data: SaveMedicine, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    medicine = db.query(Medicine).filter(Medicine.id == data.medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    saved = SavedMedicine(user_id=user.id, medicine_id=medicine.id)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return {"message": "Medicine saved"}

@router.get("/saved/{username}")
def get_saved(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    saved = db.query(SavedMedicine).filter(SavedMedicine.user_id == user.id).all()
    medicines = [db.query(Medicine).filter(Medicine.id == s.medicine_id).first() for s in saved]
    return {"saved": [{"id": m.id, "name": m.name, "generic": m.generic, "company": m.company, "price": m.price} for m in medicines if m]} 