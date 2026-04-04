from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
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


@router.get("/summary", summary="Financial summary")
async def summary(
    date_from: Optional[datetime] = Query(None, description="ISO 8601 start date"),
    date_to: Optional[datetime] = Query(None, description="ISO 8601 end date"),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin", "analyst", "viewer"])),
):
    """All roles. Total income, expense, net balance. Supports date range filter."""
    return await get_summary(db, date_from, date_to)


@router.get("/categories", summary="Category breakdown")
async def categories(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin", "analyst"])),
):
    """Admin and analyst. Per-category totals. Supports date range filter."""
    return await get_category_breakdown(db, date_from, date_to)


@router.get("/trends", summary="Monthly trends")
async def trends(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin", "analyst"])),
):
    """Admin and analyst. Monthly income/expense breakdown. Supports date range filter."""
    return await get_monthly_trends(db, date_from, date_to)


@router.get("/recent", summary="Recent activity")
async def recent(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin", "analyst", "viewer"])),
):
    """All roles. Last 10 records."""
    return await get_recent_activity(db)