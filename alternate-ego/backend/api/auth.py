"""Authentication API — register, login, and JWT-based session management."""
import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import bcrypt
import jwt

from db.database import (
    create_auth_account,
    get_auth_account_by_email,
    get_auth_account_by_id,
    update_auth_account,
    get_twin,
)
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer(auto_error=False)


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    account_id: str
    email: str
    user_id: Optional[str] = None
    twin_id: Optional[str] = None
    has_twin: bool = False
    twin_status: str = ""


# ── JWT helpers ───────────────────────────────────────────────────────────────

def _create_token(account_id: str) -> str:
    payload = {
        "sub": account_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_account(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency — extract and validate JWT, return account dict."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    payload = _decode_token(credentials.credentials)
    account = get_auth_account_by_id(payload["sub"])
    if not account:
        raise HTTPException(status_code=401, detail="Account not found")
    return account


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest):
    """Register a new account with email + password."""
    email = req.email.lower().strip()

    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    existing = get_auth_account_by_email(email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    pw_hash = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
    account_id = str(uuid.uuid4())
    create_auth_account(account_id, email, pw_hash)

    token = _create_token(account_id)
    return AuthResponse(
        token=token,
        account_id=account_id,
        email=email,
        has_twin=False,
    )


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    """Login with email + password, returns JWT token."""
    email = req.email.lower().strip()
    account = get_auth_account_by_email(email)

    if not account:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not bcrypt.checkpw(req.password.encode(), account["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = _create_token(account["id"])
    twin_id = account.get("twin_id")
    has_twin = False
    twin_status = ""
    if twin_id:
        twin = get_twin(twin_id)
        if twin:
            twin_status = twin.get("status", "")
            has_twin = twin_status in ("ready", "active")

    return AuthResponse(
        token=token,
        account_id=account["id"],
        email=account["email"],
        user_id=account.get("user_id"),
        twin_id=twin_id,
        has_twin=has_twin,
        twin_status=twin_status,
    )


@router.get("/me", response_model=AuthResponse)
async def get_me(account: dict = Depends(get_current_account)):
    """Get current authenticated account info."""
    twin_id = account.get("twin_id")
    has_twin = False
    twin_status = ""
    if twin_id:
        twin = get_twin(twin_id)
        if twin:
            twin_status = twin.get("status", "")
            has_twin = twin_status in ("ready", "active")

    return AuthResponse(
        token="",  # Don't re-issue token in /me
        account_id=account["id"],
        email=account["email"],
        user_id=account.get("user_id"),
        twin_id=twin_id,
        has_twin=has_twin,
        twin_status=twin_status,
    )


@router.post("/link-twin")
async def link_twin(
    user_id: str,
    twin_id: str,
    account: dict = Depends(get_current_account),
):
    """Link a user_id and twin_id to the current auth account."""
    update_auth_account(account["id"], user_id=user_id, twin_id=twin_id)
    return {"status": "linked", "user_id": user_id, "twin_id": twin_id}
