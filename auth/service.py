from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.supabase import supabase
from db.models import Profile


async def register(email: str, password: str, db: AsyncSession) -> dict:
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
    except Exception as e:
        error_msg = str(e).lower()
        if "rate limit" in error_msg:
            raise HTTPException(
                status_code=429,
                detail="Too many registration attempts. Wait a few minutes and try again."
            )
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")

    user = response.user
    if not user:
        raise HTTPException(status_code=400, detail="Registration failed — check your Supabase email settings")

    result = await db.execute(select(Profile).where(Profile.id == user.id))
    profile = result.scalar_one_or_none()

    if not profile:
        profile = Profile(
            id=user.id,
            email=email,
            role="viewer",
            status="active",
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    return {
        "id": profile.id,
        "email": profile.email,
        "role": profile.role,
        "message": "Registration successful.",
    }


async def login(email: str, password: str, db: AsyncSession) -> dict:
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

    session = response.session
    user = response.user

    if not session or not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    result = await db.execute(select(Profile).where(Profile.id == user.id))
    profile = result.scalar_one_or_none()

    if not profile:
        profile = Profile(id=user.id, email=email, role="viewer", status="active")
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    return {
        "user_id": profile.id,
        "email": profile.email,
        "access_token": session.access_token,
        "token_type": "bearer",
        "role": profile.role,
    }