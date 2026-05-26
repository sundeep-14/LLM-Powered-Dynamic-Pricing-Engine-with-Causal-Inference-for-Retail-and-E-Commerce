"""
schemas/user.py
---------------
Pydantic schemas for User.

3 types of schemas:
- Create  → data coming IN when registering
- Update  → data coming IN when editing
- Response → data going OUT (never expose password!)
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ── REQUEST SCHEMAS (data coming IN) ──────────────────────────────

class UserCreate(BaseModel):
    """Used when registering a new user."""
    username: str
    email: EmailStr        # Pydantic validates email format automatically
    password: str          # plain text here — repo will hash it before saving
    role_id: int


class UserLogin(BaseModel):
    """Used when a user logs in."""
    username: str
    password: str


class UserUpdate(BaseModel):
    """Used when updating profile. All fields optional — update only what's sent."""
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


# ── RESPONSE SCHEMAS (data going OUT) ─────────────────────────────

class UserResponse(BaseModel):
    """
    What we send back after creating or fetching a user.
    Notice: NO password field — never expose hashed_password!
    """
    id: int
    username: str
    email: str
    is_active: bool
    role_id: int
    created_at: datetime

    class Config:
        from_attributes = True  # allows reading from SQLAlchemy model objects


class TokenResponse(BaseModel):
    """JWT token returned after successful login."""
    access_token: str
    token_type: str = "bearer"