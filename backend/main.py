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

# Deployed frontend lives on Vercel; fall back to that URL when env var missing
DEFAULT_FRONTEND_URL = "https://ai-email-assistant-pxbe.vercel.app"
FRONTEND_URL = os.getenv("FRONTEND_URL", DEFAULT_FRONTEND_URL)

# Session middleware (for OAuth state)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("JWT_SECRET_KEY")
)

# CORS middleware
allowed_origins = {
    DEFAULT_FRONTEND_URL,
    FRONTEND_URL,
    "https://ai-email-assistant-g4go.onrender.com",  # backend self-calls during OAuth redirects
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(allowed_origins),
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

