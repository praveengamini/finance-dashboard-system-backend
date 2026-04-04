from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Record


async def get_summary(db: AsyncSession) -> dict:
    """Total income, total expense, net balance."""
    result = await db.execute(
        select(Record.type, func.sum(Record.amount).label("total"))
        .where(Record.is_deleted == False)
        .group_by(Record.type)
    )
    rows = result.all()

    totals = {"income": 0.0, "expense": 0.0}
    for row in rows:
        totals[row.type] = float(row.total)

    return {
        "total_income": totals["income"],
        "total_expense": totals["expense"],
        "net_balance": totals["income"] - totals["expense"],
    }


async def get_category_breakdown(db: AsyncSession) -> list[dict]:
    """Sum of amounts grouped by category."""
    result = await db.execute(
        select(
            Record.category,
            Record.type,
            func.sum(Record.amount).label("total"),
            func.count(Record.id).label("count"),
        )
        .where(Record.is_deleted == False)
        .group_by(Record.category, Record.type)
        .order_by(func.sum(Record.amount).desc())
    )
    return [
        {"category": r.category, "type": r.type, "total": float(r.total), "count": r.count}
        for r in result.all()
    ]


async def get_monthly_trends(db: AsyncSession) -> list[dict]:
    """Monthly income and expense totals for the last 12 months."""
    result = await db.execute(
        select(
            func.date_trunc("month", Record.date).label("month"),
            Record.type,
            func.sum(Record.amount).label("total"),
        )
        .where(Record.is_deleted == False)
        .group_by("month", Record.type)
        .order_by("month")
    )
    return [
        {"month": str(r.month), "type": r.type, "total": float(r.total)}
        for r in result.all()
    ]


async def get_recent_activity(db: AsyncSession, limit: int = 10) -> list:
    """Most recent N non-deleted records."""
    result = await db.execute(
        select(Record)
        .where(Record.is_deleted == False)
        .order_by(Record.date.desc())
        .limit(limit)
    )
    return result.scalars().all()