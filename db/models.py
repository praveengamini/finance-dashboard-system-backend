import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, TIMESTAMP, Text, Date, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import enum


class Base(DeclarativeBase):
    pass


class UserRole(str, enum.Enum):
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"


class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class RecordType(str, enum.Enum):
    income = "income"
    expense = "expense"


class Profile(Base):
    """
    Mirrors Supabase auth.users via user_id (UUID string).
    Created on first login or via admin endpoints.
    """
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String, default=UserRole.viewer)
    status: Mapped[str] = mapped_column(String, default=UserStatus.active)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class Record(Base):
    """
    A single financial entry owned by a user.
    """
    __tablename__ = "records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String, nullable=False)

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )