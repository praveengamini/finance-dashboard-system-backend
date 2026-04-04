from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.rbac import require_roles
from db.dependencies import get_db
from dashboard.service import (
    get_category_breakdown,
    get_monthly_trends,
    get_recent_activity,
    get_summary,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def summary(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin", "analyst", "viewer"])),
):
    """Total income, expense, and net balance. All roles."""
    return await get_summary(db)


@router.get("/categories")
async def categories(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin", "analyst"])),
):
    """Breakdown of totals per category. Admin and Analyst only."""
    return await get_category_breakdown(db)


@router.get("/trends")
async def trends(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin", "analyst"])),
):
    """Monthly income/expense trends. Admin and Analyst only."""
    return await get_monthly_trends(db)


@router.get("/recent")
async def recent(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin", "analyst", "viewer"])),
):
    """Last 10 financial records. All roles."""
    return await get_recent_activity(db)