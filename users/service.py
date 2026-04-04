from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Profile


async def list_users(db: AsyncSession) -> list[Profile]:
    result = await db.execute(select(Profile).order_by(Profile.created_at.desc()))
    return result.scalars().all()


async def get_user(db: AsyncSession, user_id: str) -> Profile:
    result = await db.execute(select(Profile).where(Profile.id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile


async def update_role(db: AsyncSession, user_id: str, role: str) -> Profile:
    profile = await get_user(db, user_id)
    profile.role = role
    await db.commit()
    await db.refresh(profile)
    return profile


async def update_status(db: AsyncSession, user_id: str, status: str) -> Profile:
    profile = await get_user(db, user_id)
    profile.status = status
    await db.commit()
    await db.refresh(profile)
    return profile