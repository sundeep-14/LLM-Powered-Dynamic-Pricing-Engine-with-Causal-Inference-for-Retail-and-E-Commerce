from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.core.security import decode_access_token
from backend.utils.logger import logger

bearer_scheme = HTTPBearer()


# ── Current user dependency ───────────────────────────────────────────────────

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """
    Extracts and validates the Bearer token.
    Returns the user_id (sub) from the access token.
    Raises 401 if token is missing, invalid, or expired.
    """
    token = credentials.credentials
    user_id = decode_access_token(token)

    if not user_id:
        logger.warning("Invalid or expired access token presented")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_current_admin_user_id(
    user_id: str = Depends(get_current_user_id),
) -> str:
    """
    Placeholder for admin role check.
    Will be wired to DB role lookup once user model is set up (feature/database).
    """
    # TODO: query DB to confirm user has role='admin'
    return user_id