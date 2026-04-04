from sqlalchemy import text
from db.database import engine
from db.models import Base


async def check_db():
    """Verify database connectivity on startup."""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ DB connection OK")
    except Exception as e:
        print(f"❌ DB connection failed: {e}")
        raise


async def init_db():
    """Create all tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables initialized")