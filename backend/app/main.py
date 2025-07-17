from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import medicines, users, blog, assistant, kendra, essentials

app = FastAPI(title="Medicine Web App")

# CORS setup for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Placeholder for router includes
# from .api import medicines, users, blog, assistant, kendra
app.include_router(medicines.router)
app.include_router(users.router)
app.include_router(blog.router)
app.include_router(assistant.router)
app.include_router(kendra.router)
app.include_router(essentials.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Medicine Web App API"} 