from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.services.admin_service import admin_service
from backend.core.dependencies import get_current_admin_user_id

router = APIRouter()


class RoleUpdate(BaseModel):
    role: str


class ActiveUpdate(BaseModel):
    is_active: bool


@router.get("/stats")
async def system_stats(admin_id: str = Depends(get_current_admin_user_id)):
    return await admin_service.get_system_stats()


@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 50,
    admin_id: str = Depends(get_current_admin_user_id),
):
    return await admin_service.list_users(skip=skip, limit=limit)


@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    admin_id: str = Depends(get_current_admin_user_id),
):
    return await admin_service.get_user(user_id)


@router.patch("/users/{user_id}/active")
async def set_user_active(
    user_id: str,
    body: ActiveUpdate,
    admin_id: str = Depends(get_current_admin_user_id),
):
    return await admin_service.set_user_active(user_id, body.is_active)


@router.patch("/users/{user_id}/role")
async def set_user_role(
    user_id: str,
    body: RoleUpdate,
    admin_id: str = Depends(get_current_admin_user_id),
):
    return await admin_service.set_user_role(user_id, body.role)