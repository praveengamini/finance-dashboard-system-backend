"""
Run once to bootstrap an admin account:

    python seed_admin.py

Reads ADMIN_EMAIL / ADMIN_PASSWORD from .env (or environment).
Creates the Supabase auth user, then inserts a profiles row with role=admin.
"""

import asyncio
import os

from dotenv import load_dotenv
from supabase import create_client
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin1234!")


async def seed():
    # 1. Create Supabase auth user
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    try:
        resp = sb.auth.admin.create_user(
            {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD, "email_confirm": True}
        )
        user_id = resp.user.id
        print(f"✅ Supabase user created: {user_id}")
    except Exception as e:
        print(f"⚠️  Supabase user may already exist: {e}")
        # Try to get existing user id via sign-in
        resp = sb.auth.sign_in_with_password(
            {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        user_id = resp.user.id
        print(f"ℹ️  Using existing user: {user_id}")

    # 2. Upsert profile row with role=admin
    engine = create_async_engine(DATABASE_URL)
    Session = async_sessionmaker(bind=engine, expire_on_commit=False)

    # Import here to avoid circular import at module level
    from db.models import Base, Profile

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with Session() as session:
        result = await session.execute(select(Profile).where(Profile.id == user_id))
        profile = result.scalar_one_or_none()

        if not profile:
            profile = Profile(
                id=user_id,
                email=ADMIN_EMAIL,
                role="admin",
                status="active",
            )
            session.add(profile)
        else:
            profile.role = "admin"
            profile.status = "active"

        await session.commit()
        print(f"✅ Admin profile ready — email: {ADMIN_EMAIL}, role: admin")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())