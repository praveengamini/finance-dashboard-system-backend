from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Record
from records.schemas import RecordCreate, RecordUpdate


async def create_record(db: AsyncSession, data: RecordCreate, user_id: str) -> Record:
    record = Record(
        user_id=user_id,
        amount=data.amount,
        type=data.type.value,
        category=data.category,
        date=data.date or datetime.now(timezone.utc),
        notes=data.notes,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_records(
    db: AsyncSession,
    type: str | None = None,
    category: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    query = select(Record).where(Record.is_deleted == False)

    if type:
        query = query.where(Record.type == type)
    if category:
        query = query.where(Record.category == category)
    if date_from:
        query = query.where(Record.date >= date_from)
    if date_to:
        query = query.where(Record.date <= date_to)

    query = query.order_by(Record.date.desc())

    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    records = result.scalars().all()

    return {
        "page": page,
        "page_size": page_size,
        "results": records,
    }


async def get_record_by_id(db: AsyncSession, record_id: UUID) -> Record:
    result = await db.execute(
        select(Record).where(Record.id == record_id, Record.is_deleted == False)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


async def update_record(
    db: AsyncSession, record_id: UUID, data: RecordUpdate
) -> Record:
    record = await get_record_by_id(db, record_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        # unwrap enum values
        setattr(record, field, value.value if hasattr(value, "value") else value)

    record.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(record)
    return record


async def delete_record(db: AsyncSession, record_id: UUID) -> dict:
    record = await get_record_by_id(db, record_id)
    record.is_deleted = True               # soft delete
    record.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"detail": "Record deleted successfully"}