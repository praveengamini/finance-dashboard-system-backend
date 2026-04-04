from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Record


async def get_summary(
    db: AsyncSession,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> dict:
    query = select(Record.type, func.sum(Record.amount).label("total"))\
        .where(Record.is_deleted == False)

    if date_from:
        query = query.where(Record.date >= date_from)
    if date_to:
        query = query.where(Record.date <= date_to)

    query = query.group_by(Record.type)
    result = await db.execute(query)
    rows = result.all()

    totals = {"income": 0.0, "expense": 0.0}
    for row in rows:
        totals[row.type] = float(row.total)

    return {
        "total_income": totals["income"],
        "total_expense": totals["expense"],
        "net_balance": totals["income"] - totals["expense"],
        "date_from": date_from,
        "date_to": date_to,
    }


async def get_category_breakdown(
    db: AsyncSession,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> list[dict]:
    query = select(
        Record.category,
        Record.type,
        func.sum(Record.amount).label("total"),
        func.count(Record.id).label("count"),
    ).where(Record.is_deleted == False)

    if date_from:
        query = query.where(Record.date >= date_from)
    if date_to:
        query = query.where(Record.date <= date_to)

    query = query.group_by(Record.category, Record.type)\
                 .order_by(func.sum(Record.amount).desc())

    result = await db.execute(query)
    return [
        {
            "category": r.category,
            "type": r.type,
            "total": float(r.total),
            "count": r.count,
        }
        for r in result.all()
    ]


async def get_monthly_trends(
    db: AsyncSession,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> list[dict]:
    query = select(
        func.date_trunc("month", Record.date).label("month"),
        Record.type,
        func.sum(Record.amount).label("total"),
    ).where(Record.is_deleted == False)

    if date_from:
        query = query.where(Record.date >= date_from)
    if date_to:
        query = query.where(Record.date <= date_to)

    query = query.group_by("month", Record.type).order_by("month")
    result = await db.execute(query)
    return [
        {"month": str(r.month), "type": r.type, "total": float(r.total)}
        for r in result.all()
    ]


async def get_recent_activity(db: AsyncSession, limit: int = 10) -> list:
    result = await db.execute(
        select(Record)
        .where(Record.is_deleted == False)
        .order_by(Record.date.desc())
        .limit(limit)
    )
    return result.scalars().all()