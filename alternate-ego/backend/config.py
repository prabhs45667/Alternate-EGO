import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Always load .env from the backend directory, regardless of CWD
_ENV_FILE = Path(__file__).parent / ".env"

class Settings(BaseSettings):
    # ── LLM (OpenRouter) ──
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "x-ai/grok-4.1-fast"

    # ── Embeddings ──
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ── TTS (ElevenLabs) ──
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"

    # ── Database (PostgreSQL / NeonDB) ──
    DATABASE_URL: str = ""

    # ── Auth / JWT ──
    JWT_SECRET: str = "alternate-ego-jwt-secret-2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 168  # 7 days

    # ── Voice Pipeline ──
    WHISPER_MODEL: str = "base"
    USE_COQUI: bool = False

    # ── App Settings ──
    USE_LOCAL_DB: bool = False
    USE_BEAUTIFULSOUP: bool = True
    CORS_ORIGINS: str = "http://localhost:3000"

    # ── Paths ──
    STORAGE_DIR: str = "storage"
    VECTOR_STORE_PATH: str = "storage/vector_store.json"
    UPLOADS_DIR: str = "storage/uploads"
    AVATARS_DIR: str = "storage/avatars"
    VOICES_DIR: str = "storage/voices"
    AUDIO_DIR: str = "storage/audio"

    # ── Security ──
    ENCRYPTION_KEY: str = ""

    class Config:
        env_file = str(_ENV_FILE)

settings = Settings()

