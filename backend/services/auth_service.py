from typing import Optional
from fastapi import HTTPException, status

from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from backend.utils.logger import logger

# ---------------------------------------------------------------------------
# In-memory user store — TEMPORARY until feature/database lands.
# Swap every method body for async DB calls (SQLAlchemy) in that branch.
# ---------------------------------------------------------------------------
_fake_users: dict[str, dict] = {}


def _get_user_by_email(email: str) -> Optional[dict]:
    for user in _fake_users.values():
        if user["email"] == email:
            return user
    return None


def _get_user_by_id(user_id: str) -> Optional[dict]:
    return _fake_users.get(user_id)


# ── Auth service ──────────────────────────────────────────────────────────────

class AuthService:

    async def register(self, email: str, password: str, full_name: str) -> dict:
        if _get_user_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        import uuid
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "hashed_password": hash_password(password),
            "role": "user",
            "is_active": True,
        }
        _fake_users[user_id] = user
        logger.info(f"New user registered: {email} (id={user_id})")

        return self._build_token_response(user_id)

    async def login(self, email: str, password: str) -> dict:
        user = _get_user_by_email(email)

        if not user or not verify_password(password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )

        logger.info(f"User logged in: {email}")
        return self._build_token_response(user["id"])

    async def refresh(self, refresh_token: str) -> dict:
        user_id = decode_refresh_token(refresh_token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user = _get_user_by_id(user_id)
        if not user or not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        logger.info(f"Tokens refreshed for user_id={user_id}")
        return self._build_token_response(user_id)

    async def get_profile(self, user_id: str) -> dict:
        user = _get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "is_active": user["is_active"],
        }

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _build_token_response(user_id: str) -> dict:
        return {
            "access_token": create_access_token(user_id),
            "refresh_token": create_refresh_token(user_id),
            "token_type": "bearer",
        }


auth_service = AuthService()