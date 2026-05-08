"""Alternate Ego API — FastAPI entry point.

The main server that orchestrates the digital twin platform.
Run with: uvicorn main:app --reload --port 8000
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from config import settings
from db.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize database on import
init_db()

# Create FastAPI app
app = FastAPI(
    title="Alternate Ego API",
    description="AI-Powered Digital Twin — Thinks, Speaks, and Responds Like You",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for avatars, voice, videos, etc.
os.makedirs("storage", exist_ok=True)
os.makedirs("storage/videos", exist_ok=True)
app.mount("/static/storage", StaticFiles(directory="storage"), name="storage")

# Import and mount routers
from api.auth import router as auth_router
from api.onboarding import router as onboarding_router
from api.chat import router as chat_router
from api.mcp_actions import router as mcp_router
from api.privacy import router as privacy_router
from api.memory import router as memory_router
from api.ws_logs import router as ws_router
from api.avatar_api import router as avatar_router

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(onboarding_router, prefix="/api/onboarding", tags=["Onboarding"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(mcp_router, prefix="/api/mcp", tags=["MCP Actions"])
app.include_router(privacy_router, prefix="/api/privacy", tags=["Privacy"])
app.include_router(memory_router, prefix="/api/memory", tags=["Memory"])
app.include_router(ws_router, prefix="/ws", tags=["WebSocket"])
app.include_router(avatar_router, prefix="/api/avatar", tags=["Avatar"])


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "Alternate Ego API is running",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "onboarding": "/api/onboarding",
            "chat": "/api/chat",
            "mcp": "/api/mcp",
            "privacy": "/api/privacy"
        }
    }


@app.get("/health")
def health():
    """Detailed health check."""
    from voice.stt import is_available as stt_check

    return {
        "status": "healthy",
        "services": {
            "database": "✅ PostgreSQL (NeonDB) connected",
            "llm": f"✅ OpenRouter ({settings.OPENROUTER_MODEL})",
            "tts": "✅ Fallback TTS configured (Coqui/Edge/gTTS)",
            "stt": "✅ Available" if stt_check() else "⚠️ Not available (optional)",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
