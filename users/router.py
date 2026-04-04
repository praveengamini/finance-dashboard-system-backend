from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.rbac import require_roles
from db.dependencies import get_db
from users.schemas import UserResponse, UserRoleUpdate, UserStatusUpdate
from users.service import get_user, list_users, update_role, update_status

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
async def all_users(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin"])),
):
    """List all users. Admin only."""
    return await list_users(db)


@router.get("/{user_id}", response_model=UserResponse)
async def single_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin"])),
):
    """Get a single user by ID. Admin only."""
    return await get_user(db, user_id)


@router.patch("/{user_id}/role", response_model=UserResponse)
async def change_role(
    user_id: str,
    payload: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin"])),
):
    """Assign a new role to a user. Admin only."""
    return await update_role(db, user_id, payload.role.value)


@router.patch("/{user_id}/status", response_model=UserResponse)
async def change_status(
    user_id: str,
    payload: UserStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin"])),
):
    """Activate or deactivate a user. Admin only."""
    return await update_status(db, user_id, payload.status.value)