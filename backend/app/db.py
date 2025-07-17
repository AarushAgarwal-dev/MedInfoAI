from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Use SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medicine_db.sqlite3")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 