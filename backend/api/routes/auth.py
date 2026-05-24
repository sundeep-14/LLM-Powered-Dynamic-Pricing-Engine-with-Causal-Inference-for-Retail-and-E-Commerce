from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field

from backend.services.auth_service import auth_service
from backend.core.dependencies import get_current_user_id

router = APIRouter()


# ── Request / Response schemas ────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest):
    """Register a new user and return access + refresh tokens."""
    return await auth_service.register(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    """Authenticate and return access + refresh tokens."""
    return await auth_service.login(email=body.email, password=body.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest):
    """Exchange a valid refresh token for a new token pair."""
    return await auth_service.refresh(refresh_token=body.refresh_token)


@router.get("/me", response_model=UserProfile)
async def get_profile(user_id: str = Depends(get_current_user_id)):
    """Return the currently authenticated user's profile."""
    return await auth_service.get_profile(user_id=user_id)


@router.post("/logout", status_code=204)
async def logout(user_id: str = Depends(get_current_user_id)):
    """
    Stateless logout — client discards tokens.
    Token blacklisting can be added here (Redis) when needed.
    """
    return None