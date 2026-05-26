from fastapi import HTTPException, status
from backend.utils.helpers import utcnow_iso
from backend.utils.logger import logger

# Reference to auth service's user store
from backend.services.auth_service import _fake_users


class AdminService:

    async def list_users(self, skip: int = 0, limit: int = 50) -> list:
        users = list(_fake_users.values())
        return [self._safe_user(u) for u in users[skip: skip + limit]]

    async def get_user(self, user_id: str) -> dict:
        user = _fake_users.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return self._safe_user(user)

    async def set_user_active(self, user_id: str, is_active: bool) -> dict:
        user = _fake_users.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        user["is_active"] = is_active
        action = "activated" if is_active else "deactivated"
        logger.info(f"User {action}: id={user_id}")
        return self._safe_user(user)

    async def set_user_role(self, user_id: str, role: str) -> dict:
        user = _fake_users.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        user["role"] = role
        logger.info(f"User role updated: id={user_id} role={role}")
        return self._safe_user(user)

    async def get_system_stats(self) -> dict:
        from backend.services.product_service import _products
        from backend.services.report_service import _reports
        return {
            "total_users": len(_fake_users),
            "active_users": sum(1 for u in _fake_users.values() if u["is_active"]),
            "total_products": len(_products),
            "total_reports": len(_reports),
            "generated_at": utcnow_iso(),
        }

    @staticmethod
    def _safe_user(user: dict) -> dict:
        return {k: v for k, v in user.items() if k != "hashed_password"}


admin_service = AdminService()