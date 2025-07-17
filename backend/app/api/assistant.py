from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/assistant", tags=["assistant"])

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat(request: ChatRequest):
    # Placeholder: Replace with Groq API call
    return {"response": f"AI says: You asked '{request.message}'"} 