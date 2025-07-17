from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    saved_medicines = relationship('SavedMedicine', back_populates='user')

class Medicine(Base):
    __tablename__ = 'medicines'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    generic = Column(String, index=True, nullable=False)
    company = Column(String)
    price = Column(Float)

class SavedMedicine(Base):
    __tablename__ = 'saved_medicines'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    medicine_id = Column(Integer, ForeignKey('medicines.id'))
    user = relationship('User', back_populates='saved_medicines')
    medicine = relationship('Medicine')

class BlogPost(Base):
    __tablename__ = 'blog_posts'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)

class Kendra(Base):
    __tablename__ = 'kendras'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False) 