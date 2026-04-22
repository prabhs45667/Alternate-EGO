# 🛠️ Alternate Ego — Final Implementation Guide

> **Everything in one place.** Architecture, code, privacy, free alternatives, and step-by-step execution.

---

## 📋 Table of Contents

1. [Tech Stack (All Free)](#1-tech-stack-all-free)
2. [Project Structure](#2-project-structure)
3. [Phase 1: Foundation + Server](#3-phase-1-foundation--server)
4. [Phase 2: Database (SQLite)](#4-phase-2-database)
5. [Phase 3: RAG Brain (Embeddings + Vector Store)](#5-phase-3-rag-brain)
6. [Phase 4: Social Scraping + Data Upload](#6-phase-4-social-scraping--data-upload)
7. [Phase 5: Avatar (4 Emotion Photos + CV)](#7-phase-5-avatar-generation)
8. [Phase 6: Voice Pipeline (STT + TTS)](#8-phase-6-voice-pipeline)
9. [Phase 7: Chat API + Slash Commands](#9-phase-7-chat--slash-commands)
10. [Phase 8: Privacy & Security Layer](#10-phase-8-privacy--security)
11. [Phase 9: Next.js Frontend](#11-phase-9-nextjs-frontend)
12. [Running the Project](#12-running-the-project)

---

## 1. Tech Stack (All Free)

| Component | Tool | Cost |
|---|---|---|
| **Backend** | FastAPI + Uvicorn | ₹0 |
| **Frontend** | Next.js 14 + TailwindCSS | ₹0 |
| **Database** | SQLite (local) | ₹0 |
| **Vector Store** | Pure Python JSON Engine (custom) | ₹0 |
| **Embeddings** | `nomic-embed-text` via Ollama | ₹0 |
| **LLM** | `llama3.1:8b` via Ollama | ₹0 |
| **STT** | `faster-whisper` (local CPU) | ₹0 |
| **TTS / Voice Clone** | Coqui XTTS v2 (local) | ₹0 |
| **Social Scraping** | BeautifulSoup + DuckDuckGo | ₹0 |
| **CV Emotion Detection** | `face-api.js` (browser-side) | ₹0 |
| **Encryption** | `cryptography.fernet` (Python) | ₹0 |
| **Total** | **₹0** | ✅ |

### Why These Choices?
- **No ChromaDB** → caused `hnswlib` DLL crashes on Windows. Replaced with Pure Python JSON vector store.
- **No sentence-transformers** → caused `c10.dll` PyTorch crash. Replaced with Ollama `nomic-embed-text`.
- **No paid APIs** → Every single component runs locally on the user's machine.

---

## 2. Project Structure

```
alternate-ego/
├── backend/
│   ├── main.py                         # FastAPI entry point
│   ├── config.py                       # Environment settings
│   ├── .env                            # API keys & config
│   ├── requirements.txt
│   ├── api/
│   │   ├── __init__.py
│   │   ├── onboarding.py              # /api/onboarding/* (name, photos, voice, upload-data)
│   │   ├── chat.py                     # /api/chat/message (RAG + LLM)
│   │   ├── mcp_actions.py             # /api/mcp/* (social actions)
│   │   └── privacy.py                 # /api/privacy/* (delete data, data summary)
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── chunker.py                 # Split text into topic chunks
│   │   ├── embedder.py                # Ollama nomic-embed-text embeddings
│   │   ├── vector_store.py            # Pure Python JSON cosine similarity engine
│   │   ├── prompt_builder.py          # Build system prompt + RAG context
│   │   ├── llm.py                     # Ollama llama3.1 LLM calls
│   │   ├── scrape_processor.py        # Web scraping + .zip/.json export parser
│   │   ├── transcript_processor.py    # Voice transcript → RAG chunks
│   │   └── source_tracker.py          # Format RAG citations
│   ├── voice/
│   │   ├── __init__.py
│   │   ├── stt.py                     # Speech-to-Text (faster-whisper)
│   │   ├── tts.py                     # Text-to-Speech (Coqui XTTS v2)
│   │   └── voice_manager.py           # Manage cloned voice references
│   ├── avatar/
│   │   ├── __init__.py
│   │   └── avatar_generator.py        # Save 4 emotion photos, select avatar
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── slash_parser.py            # Parse /platform action content
│   │   └── social_poster.py           # Simulated social media posting
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py                # SQLite init + 5 tables
│   │   └── models.py                  # Pydantic data models
│   ├── security/
│   │   ├── __init__.py
│   │   └── encryption.py              # Fernet encrypt/decrypt/secure-delete
│   └── storage/
│       ├── avatars/{twin_id}/         # Emotion photos
│       ├── voices/{twin_id}/          # Voice reference audio
│       └── uploads/{twin_id}/         # Encrypted uploaded data (auto-deleted)
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── globals.css            # Glassmorphism + mountain background
│   │   │   ├── layout.tsx             # Root layout (Playfair + Inter fonts)
│   │   │   ├── page.tsx               # Landing (name + social URLs + privacy consent)
│   │   │   ├── onboarding/
│   │   │   │   └── page.tsx           # Photos (CV) → Voice Interview → Generating
│   │   │   └── chat/
│   │   │       └── page.tsx           # Split-screen: Avatar + Chat
│   │   ├── components/
│   │   │   ├── NameInput.tsx           # Name input field
│   │   │   ├── PrivacyBanner.tsx       # "Your data is encrypted & never shared"
│   │   │   ├── DataUpload.tsx          # Drag-drop .zip/.json upload
│   │   │   ├── CameraCapture.tsx       # Webcam + face-api.js emotion detection
│   │   │   ├── VoiceInterview.tsx      # 9 questions, MediaRecorder API
│   │   │   ├── GeneratingScreen.tsx    # Loading animation
│   │   │   ├── ScrapingScreen.tsx      # "Scraping social media..."
│   │   │   ├── AvatarView.tsx          # Avatar display (left panel)
│   │   │   ├── ChatWindow.tsx          # Chat messages
│   │   │   ├── SourceCitations.tsx     # RAG source pills
│   │   │   └── AudioPlayer.tsx         # TTS voice playback
│   │   └── lib/
│   │       ├── api.ts                  # Backend API client
│   │       ├── camera.ts              # Webcam utilities
│   │       └── audio.ts               # Audio recording utilities
│   ├── public/
│   │   └── models/                    # face-api.js TensorFlow weights
│   └── package.json
│
├── XTTS-v2/                           # Coqui voice cloning model (~2GB)
└── README.md
```

---

## 3. Phase 1: Foundation + Server

### What It Does
Sets up the full Python backend: virtual environment, FastAPI server, CORS, routing.

### Files
```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.onboarding import router as onboarding_router  # type: ignore
from api.chat import router as chat_router              # type: ignore
from api.mcp_actions import router as mcp_router        # type: ignore
from api.privacy import router as privacy_router        # type: ignore

app = FastAPI(title="Alternate Ego API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(onboarding_router, prefix="/api/onboarding", tags=["Onboarding"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(mcp_router, prefix="/api/mcp", tags=["MCP"])
app.include_router(privacy_router, prefix="/api/privacy", tags=["Privacy"])

@app.get("/")
def root():
    return {"status": "Alternate Ego API is running", "version": "2.0.0"}
```

```python
# backend/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_MODEL: str = "llama3.1:8b"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    USE_COQUI: bool = True
    WHISPER_MODEL: str = "base"
    USE_LOCAL_DB: bool = True
    USE_BEAUTIFULSOUP: bool = True
    ENCRYPTION_KEY: str = ""  # Auto-generated if empty

    class Config:
        env_file = ".env"

settings = Settings()
```

### Setup Commands
```bash
mkdir alternate-ego && cd alternate-ego
mkdir -p backend/{api,rag,voice,avatar,mcp,db,security,storage}
cd backend
python -m venv venv
venv\Scripts\activate  # Windows

pip install fastapi uvicorn python-dotenv pydantic pydantic-settings \
  python-multipart aiofiles websockets Pillow beautifulsoup4 requests \
  ollama faster-whisper TTS cryptography

pip freeze > requirements.txt
```

### Verify
```bash
uvicorn main:app --reload --port 8000
# Visit http://localhost:8000 → {"status": "Alternate Ego API is running"}
# Visit http://localhost:8000/docs → Swagger API docs
```

---

## 4. Phase 2: Database

### What It Does
Creates SQLite database with 5 tables for users, twins, conversations, messages, and onboarding sessions.

### File: `backend/db/database.py`
```python
import sqlite3
DB_PATH = "ego_database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS twins (
            id TEXT PRIMARY KEY,
            user_id TEXT REFERENCES users(id),
            voice_model_path TEXT,
            photo_neutral TEXT, photo_happy TEXT, photo_sad TEXT, photo_angry TEXT,
            avatar_path TEXT, personality_profile TEXT, system_prompt TEXT,
            scraped_data TEXT, status TEXT DEFAULT 'creating',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            twin_id TEXT REFERENCES twins(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT REFERENCES conversations(id),
            role TEXT NOT NULL, content TEXT NOT NULL, sources TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS onboarding_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT REFERENCES users(id),
            scraping_status TEXT DEFAULT 'pending',
            photos_captured INTEGER DEFAULT 0,
            questions_answered INTEGER DEFAULT 0,
            status TEXT DEFAULT 'in_progress',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

init_db()
```

### File: `backend/db/models.py`
```python
from pydantic import BaseModel
from typing import Optional, List

class StartRequest(BaseModel):
    name: str

class ChatRequest(BaseModel):
    twin_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    sources: List[dict] = []
    is_action: bool = False

class TwinPersonality(BaseModel):
    name: str
    tone: str = "friendly, authentic, conversational"
    interests: str = "technology, social media, learning"
    background: str = ""
    speech_style: str = "casual and natural"
```

---

## 5. Phase 3: RAG Brain

### What It Does
The "brain" of the digital twin. Ingests data → generates embeddings → stores vectors → retrieves relevant context → builds LLM prompts.

### Key Decision: Why No ChromaDB?
ChromaDB uses `hnswlib` (C++ compiled) which crashes on Windows with `DLL load failed`. Replaced with a **Pure Python JSON Vector Store** using native `math.sqrt()` cosine similarity.

### File: `backend/rag/embedder.py`
```python
# Uses Ollama nomic-embed-text (NOT sentence-transformers — DLL crash)
import requests

def generate_embedding(text: str) -> list:
    response = requests.post("http://localhost:11434/api/embeddings", json={
        "model": "nomic-embed-text",
        "prompt": text
    })
    return response.json()["embedding"]  # 768-dimensional vector
```

### File: `backend/rag/vector_store.py`
```python
# Pure Python JSON engine — zero external DLLs
import json, os, math, uuid

STORE_PATH = "simple_vectors.json"

def _cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0

def add_chunks(twin_id, chunks):
    # Generate embeddings → store in JSON with metadata

def search(twin_id, query, top_k=5):
    # Embed query → cosine similarity → return top_k matches
```

### File: `backend/rag/prompt_builder.py`
```python
def build_system_prompt(twin_id, personality):
    return f"""You are the digital twin of {personality.get('name', 'User')}.
    You must respond as if you ARE this person — first person only.
    RULES:
    1. Always speak in first person ("I am...", "I think...")
    2. Never say you are an AI or digital twin
    3. Be authentic to the personality described"""

def build_chat_prompt(twin_id, user_message, system_prompt):
    # Search RAG → Build context → Return messages + sources
```

### File: `backend/rag/llm.py`
```python
import ollama

def generate_response(messages):
    response = ollama.chat(model="llama3.1:8b", messages=messages)
    return response["message"]["content"]
```

### Prerequisites
```bash
# Install Ollama from https://ollama.ai
ollama pull nomic-embed-text
ollama pull llama3.1:8b
```

---

## 6. Phase 4: Social Scraping + Data Upload

### What It Does
Two approaches to gather data about the user:
1. **Public Profile Scraping** — Scrape LinkedIn/Instagram/Twitter URLs with BeautifulSoup
2. **Data Export Upload** — User uploads their Instagram/LinkedIn `.zip`/`.json` export file

### Why Data Export?
- Private accounts CANNOT be scraped (login wall blocks it)
- OAuth APIs are heavily restricted (Instagram = Business only, LinkedIn = Partnership needed)
- Data export gives 100% data, legally, including private content

### File: `backend/rag/scrape_processor.py`
```python
import requests, json, zipfile, os
from bs4 import BeautifulSoup
from rag.chunker import chunk_by_topic
from rag.vector_store import add_chunks

def scrape_and_index(name, twin_id, social_urls=None):
    """Scrape public profiles + general web mentions."""
    all_chunks = []

    # 1. Scrape provided direct URLs
    if social_urls:
        for url in social_urls:
            if url.strip():
                text = scrape_public_profile(url.strip())
                chunks = chunk_by_topic(text, "social_profile", url)
                all_chunks.extend(chunks)

    # 2. DuckDuckGo general search
    for query in [f"{name} LinkedIn", f"{name} about"]:
        # ... DuckDuckGo scraping logic ...

    if all_chunks:
        add_chunks(twin_id, all_chunks)
    return {"chunks_indexed": len(all_chunks)}

def parse_instagram_export(zip_path, twin_id):
    """Parse Instagram data export .zip file."""
    all_chunks = []
    with zipfile.ZipFile(zip_path, 'r') as z:
        for fname in z.namelist():
            if fname.endswith('.json'):
                data = json.loads(z.read(fname))
                # Extract posts, captions, comments, bio...
                # Chunk and index each piece
    add_chunks(twin_id, all_chunks)
    return {"chunks_indexed": len(all_chunks)}

def parse_linkedin_export(zip_path, twin_id):
    """Parse LinkedIn data export .zip file."""
    # Similar: extract profile, positions, skills, recommendations, posts
```

### Privacy Protection for Uploads
```
User uploads .zip → Backend encrypts it → Parses content → Feeds to RAG → DELETES raw file
                                                                              ↑
                                                              Only embeddings remain (not reversible)
```

---

## 7. Phase 5: Avatar Generation

### What It Does
Captures 4 emotion photos (neutral, happy, sad, angry) using the webcam. **Computer Vision validates** the user's expression before allowing capture.

### CV Emotion Detection (face-api.js)
```
Browser loads face-api.js TensorFlow.js models
    ↓
Real-time video frame analysis every 500ms
    ↓
Detects face → Classifies expression (neutral/happy/sad/angry/surprised)
    ↓
If expression MATCHES required emotion → ✅ Allow capture
If expression DOESN'T match → ❌ Block capture + show warning
```

### Frontend Implementation
```javascript
// face-api.js runs IN THE BROWSER (no server needed)
import * as faceapi from 'face-api.js';

// Load models from /public/models/
await faceapi.nets.tinyFaceDetector.loadFromUri('/models');
await faceapi.nets.faceLandmark68Net.loadFromUri('/models');
await faceapi.nets.faceExpressionNet.loadFromUri('/models');

// Real-time detection loop
const detection = await faceapi
  .detectSingleFace(videoElement, new faceapi.TinyFaceDetectorOptions())
  .withFaceLandmarks()
  .withFaceExpressions();

// detection.expressions = { neutral: 0.8, happy: 0.1, sad: 0.05, angry: 0.05 }
```

### Backend: `backend/avatar/avatar_generator.py`
```python
def save_photos(twin_id, photos):
    """Save 4 emotion photos. Use neutral as avatar."""
    twin_dir = f"storage/avatars/{twin_id}"
    os.makedirs(twin_dir, exist_ok=True)
    for emotion, photo_bytes in photos.items():
        path = os.path.join(twin_dir, f"{emotion}.jpg")
        with open(path, "wb") as f:
            f.write(photo_bytes)
    return {"avatar_path": f"{twin_dir}/neutral.jpg"}
```

---

## 8. Phase 6: Voice Pipeline

### What It Does
1. **STT (Speech-to-Text):** User answers 9 questions via voice → `faster-whisper` transcribes locally
2. **TTS (Text-to-Speech):** Coqui XTTS v2 clones the user's voice → Digital twin speaks in their voice

### 9 Interview Questions
```python
QUESTIONS = [
    "Tell me about yourself — your background, work, and passions.",
    "What are your core values and beliefs?",
    "How do your friends describe you?",
    "What's a story that shaped who you are today?",
    "What's your biggest achievement you're proud of?",
    "How do you handle stress or difficult situations?",
    "What makes you laugh or brings you joy?",
    "What are your goals for the next few years?",
    "If you could give advice to your younger self, what would it be?"
]
```

### File: `backend/voice/stt.py`
```python
from faster_whisper import WhisperModel

_whisper = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe(audio_path):
    segments, _ = _whisper.transcribe(audio_path, language="en")
    return " ".join([seg.text for seg in segments]).strip()
```

### File: `backend/voice/tts.py`
```python
from TTS.api import TTS

# IMPORTANT: First run downloads ~2GB model
_tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

def generate_speech(twin_id, text):
    ref_path = f"storage/voices/{twin_id}/reference.wav"
    output_path = f"storage/voices/{twin_id}/output.wav"
    _tts.tts_to_file(text=text, speaker_wav=ref_path, language="en", file_path=output_path)
    return output_path
```

### Coqui XTTS Setup
```bash
# Already downloaded via:
git clone https://huggingface.co/coqui/XTTS-v2   # ~2GB, stored at ego/XTTS-v2/
```

---

## 9. Phase 7: Chat + Slash Commands

### What It Does
RAG-powered chat where the digital twin answers questions using all ingested data. Supports `/slash commands` for social media actions.

### Chat Flow
```
User: "What do you do for work?"
    ↓
1. Check for /slash command → No
2. Search RAG vector store → Find relevant chunks about career
3. Build system prompt + context
4. Send to Ollama llama3.1:8b
5. Return response + source citations
    ↓
Twin: "I'm a software developer who loves building AI projects..."
    Sources: [🌐 LinkedIn, 🎙️ Voice Answer Q1]
```

### Slash Commands
```
/linkedin post "Just launched my digital twin!"
    → ✅ Posted to LinkedIn: "Just launched my digital twin!"

/twitter post "Hello world from my AI clone"
    → ✅ Posted to Twitter: "Hello world from my AI clone"
```

---

## 10. Phase 8: Privacy & Security

### The Promise to Users
```
🔒 Your data is encrypted, processed locally on your device, and NEVER shared with anyone.
📱 We do not store your personal data permanently.
🗑️ You can delete ALL your data at any time.
```

### File: `backend/security/encryption.py`
```python
from cryptography.fernet import Fernet
import os

def get_or_create_key():
    key_path = "storage/.encryption_key"
    if os.path.exists(key_path):
        return open(key_path, "rb").read()
    key = Fernet.generate_key()
    with open(key_path, "wb") as f:
        f.write(key)
    return key

_fernet = Fernet(get_or_create_key())

def encrypt_file(file_path):
    with open(file_path, "rb") as f:
        encrypted = _fernet.encrypt(f.read())
    with open(file_path + ".enc", "wb") as f:
        f.write(encrypted)
    os.remove(file_path)  # Delete plaintext
    return file_path + ".enc"

def delete_securely(twin_id):
    """Wipe ALL data for a twin: photos, voice, vectors, uploads."""
    import shutil
    for folder in ["avatars", "voices", "uploads"]:
        path = f"storage/{folder}/{twin_id}"
        if os.path.exists(path):
            shutil.rmtree(path)
    # Also remove from vector store JSON
```

### File: `backend/api/privacy.py`
```python
from fastapi import APIRouter
from security.encryption import delete_securely

router = APIRouter()

@router.delete("/delete-all/{twin_id}")
async def delete_all_data(twin_id: str):
    delete_securely(twin_id)
    return {"status": "All data for this twin has been permanently deleted"}

@router.get("/data-summary/{twin_id}")
async def data_summary(twin_id: str):
    return {
        "photos_stored": 4,
        "voice_samples": 1,
        "rag_chunks": "...",
        "message": "You can delete all data anytime using the Delete button"
    }
```

### Data Lifecycle
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User Upload │ ──→ │  Encrypted   │ ──→ │  Parsed &    │ ──→ │  Raw File    │
│  .zip/.json  │     │  on Disk     │     │  Fed to RAG  │     │  DELETED     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                      │
                                                                      ▼
                                                          Only embeddings remain
                                                          (not human-readable)
```

---

## 11. Phase 9: Next.js Frontend

### Design Aesthetic (From Screenshots)
- 🏔️ **Background**: Majestic mountain landscape
- 🪟 **Glassmorphism**: Frosted-glass panels (`backdrop-filter: blur(20px)`)
- 🖋️ **Typography**: Playfair Display (serif, elegant) + Inter (clean sans-serif)
- 🎨 **Colors**: Deep purple/indigo gradients, white-on-glass text, green accent buttons

### User Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Landing Page                                          │
│  ┌──────────────────────────────────────┐                      │
│  │         ✦ Ego ✦                      │                      │
│  │    [Enter your name: ________]       │                      │
│  │    LinkedIn URL: ____________        │                      │
│  │    Instagram: @_____________         │                      │
│  │    Twitter: @_______________         │                      │
│  │    [Upload Social Data .zip] 📎      │                      │
│  │                                      │                      │
│  │    🔒 Your data is encrypted and     │                      │
│  │       never shared with anyone.      │                      │
│  │    ☑ I consent to data processing    │                      │
│  │                                      │                      │
│  │    [UPLOAD YOURSELF →]               │                      │
│  └──────────────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Photo Capture (4 Emotions + CV Validation)            │
│  ┌──────────────────────────────────────┐                      │
│  │  [Webcam Feed]    ✅ Detecting: happy│                      │
│  │                                      │                      │
│  │  "Smile naturally (happy expression)"│                      │
│  │  [1️⃣] [2️⃣] [3️⃣] [4️⃣]  ← thumbnails   │                      │
│  │                                      │                      │
│  │  ✅ AI emotion detection active      │                      │
│  │  [📷 Capture Photo]                  │                      │
│  └──────────────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Voice Interview (9 Questions)                         │
│  ┌──────────────────────────────────────┐                      │
│  │  Q1: "Tell me about yourself..."     │                      │
│  │  [🎙️ Record] [⏩ Skip]               │                      │
│  │  ①②③④⑤⑥⑦⑧⑨  ← progress              │                      │
│  └──────────────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Generating Ego...                                     │
│  ┌──────────────────────────────────────┐                      │
│  │  ⟳ Analyzing social data...          │                      │
│  │  ⟳ Processing voice patterns...      │                      │
│  │  ⟳ Building personality profile...   │                      │
│  └──────────────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Chat with Your Digital Twin                           │
│  ┌──────────┬───────────────────────────┐                      │
│  │          │  Ego Chat                 │                      │
│  │  Avatar  │  ┌────────────────────┐   │                      │
│  │  (Left)  │  │ 🤖 "Hey! I'm your │   │                      │
│  │          │  │    digital twin!"  │   │                      │
│  │  neutral │  │  [▶ Play]          │   │                      │
│  │  .jpg    │  └────────────────────┘   │                      │
│  │          │  ┌────────────────────┐   │                      │
│  │          │  │ 👤 "Who are you?" │   │                      │
│  │          │  └────────────────────┘   │                      │
│  │          │                           │                      │
│  │          │  [Type a message... 📤]   │                      │
│  └──────────┴───────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

### Frontend Setup
```bash
cd alternate-ego
npx -y create-next-app@latest frontend --typescript --tailwind --app --eslint --src-dir
cd frontend
npm install face-api.js lucide-react
```

---

## 12. Running the Project

### Prerequisites
```bash
# 1. Ollama must be installed and running
ollama serve
ollama pull nomic-embed-text
ollama pull llama3.1:8b

# 2. Coqui XTTS model downloaded (already done)
# Located at: ego/XTTS-v2/
```

### Start Everything
```bash
# Terminal 1: Backend
cd alternate-ego/backend
venv\Scripts\activate
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd alternate-ego/frontend
npm run dev

# Terminal 3: Ollama (if not already running)
ollama serve
```

### Open Browser
```
http://localhost:3000  → Frontend UI
http://localhost:8000  → Backend API
http://localhost:8000/docs  → Swagger API Documentation
```

### Demo Flow
```
1. Enter name + social URLs + upload data export
2. Accept privacy consent
3. Take 4 CV-validated emotion photos
4. Answer 9 voice interview questions
5. Wait for twin generation
6. Chat with your digital twin!
7. Try: /linkedin post "Hello from my AI twin!"
```

---

## ✅ Completion Checklist

| Phase | Status |
|---|---|
| Phase 1: Foundation | ✅ Complete |
| Phase 2: Database | ✅ Complete |
| Phase 3: RAG Brain | ✅ Complete |
| Phase 4: Scraping + Upload | ✅ Code Done |
| Phase 5: Avatar + CV | ✅ Complete |
| Phase 6: Voice Pipeline | ✅ Complete |
| Phase 7: Chat + Slash | ✅ Complete |
| Phase 8: Privacy/Security | 🔧 Needs `encryption.py` + `privacy.py` wiring |
| Phase 9: Frontend | ✅ Core pages done, needs `PrivacyBanner` + `DataUpload` |

---

> **Total Cost: ₹0** | **Everything runs locally** | **Zero external API dependencies**
