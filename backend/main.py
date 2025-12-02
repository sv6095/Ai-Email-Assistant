# FastAPI main application file
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from routers import auth, chat
import os

app = FastAPI(
    title="AI Email Assistant API",
    version="1.0.0",
    description="Backend for AI-powered email management"
)

# Session middleware (for OAuth state)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("JWT_SECRET_KEY")
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-email-assistant-zeta.vercel.app",
        os.getenv("FRONTEND_URL", "https://ai-email-assistant-zeta.vercel.app")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {
        "message": "AI Email Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

