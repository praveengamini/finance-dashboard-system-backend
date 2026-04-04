from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.rbac import require_roles
from db.dependencies import get_db
from records.schemas import RecordCreate, RecordResponse, RecordUpdate
from records.service import (
    create_record,
    delete_record,
    get_record_by_id,
    get_records,
    update_record,
)

router = APIRouter(prefix="/records", tags=["Records"])


@router.post(
    "/create",
    response_model=RecordResponse,
    status_code=201,
    summary="Create a record",
)
async def create_record_endpoint(
    payload: RecordCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin"])),
):
    """Admin only. Creates a new income or expense record."""
    return await create_record(db, payload, user["id"])


@router.get(
    "/list",
    response_model=dict,
    summary="List all records",
)
async def list_records_endpoint(
    type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin", "analyst", "viewer"])),
):
    """All roles. Filter by type, category, date range."""
    return await get_records(db, type, category, date_from, date_to, page, page_size)


@router.get(
    "/get/{record_id}",
    response_model=RecordResponse,
    summary="Get a single record",
)
async def get_record_endpoint(
    record_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin", "analyst", "viewer"])),
):
    """All roles. Fetch one record by UUID."""
    return await get_record_by_id(db, record_id)


@router.put(
    "/update/{record_id}",
    response_model=RecordResponse,
    summary="Update a record",
)
async def update_record_endpoint(
    record_id: UUID,
    payload: RecordUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin"])),
):
    """Admin only. Partial update — only sent fields are changed."""
    return await update_record(db, record_id, payload)


@router.delete(
    "/delete/{record_id}",
    summary="Delete a record",
)
async def delete_record_endpoint(
    record_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles(["admin"])),
):
    """Admin only. Soft delete."""
    return await delete_record(db, record_id)