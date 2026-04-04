import asyncio
import os
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from db.database import engine
from db.models import Base

MAX_RETRIES = 3
RETRY_DELAY = 2  


async def check_db():
    """Verify database connectivity on startup with retry logic."""
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Please configure it in your Render service settings."
        )
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            print("✅ DB connection OK")
            return
        except (OperationalError, OSError) as e:
            print(f"⚠️  DB connection attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                print(f"   Retrying in {RETRY_DELAY} seconds...")
                await asyncio.sleep(RETRY_DELAY)
            else:
                print("❌ DB connection failed after all retries")
                raise


async def init_db():
    """Create all tables if they don't exist."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables initialized")
    except Exception as e:
        print(f"⚠️  Table initialization warning: {e}")