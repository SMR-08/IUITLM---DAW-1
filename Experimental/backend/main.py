from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import db_chat_router # Import the new router
from config import GEMINI_API_KEY # Import GEMINI_API_KEY from config


app = FastAPI()

origins = [
    "http://localhost:3000",  # Allow requests from the React frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins during development to fix CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(db_chat_router.router) # Include the new router

@app.get("/")
def read_root():
    return {"Hello": "World from FastAPI"}