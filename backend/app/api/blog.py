from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import BlogPost
from typing import List

router = APIRouter(prefix="/blog", tags=["blog"])

class BlogPostIn(BaseModel):
    title: str
    content: str

@router.get("/")
def list_posts(db: Session = Depends(get_db)):
    posts = db.query(BlogPost).all()
    return {"posts": [{"id": p.id, "title": p.title, "content": p.content} for p in posts]}

@router.post("/")
def create_post(post: BlogPostIn, db: Session = Depends(get_db)):
    db_post = BlogPost(title=post.title, content=post.content)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return {"message": "Post created", "id": db_post.id} 