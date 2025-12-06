from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import User
from src.domain.ports import UserRepository


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for adapter models."""


class UserRecord(Base):
    """
    Persistence model for users.
    Stored as simple columns; domain stays Pydantic-based.
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, nullable=False)


def _to_record(user: User) -> UserRecord:
    """Translate a domain User into a persistence record."""
    return UserRecord(
        id=str(user.id),
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
    )


def _to_domain(record: UserRecord) -> User:
    """Translate a persistence record into a domain User."""
    return User.model_validate(
        {
            "id": record.id,
            "username": record.username,
            "email": record.email,
            "is_active": record.is_active,
            "created_at": record.created_at,
        }
    )


class SqlAlchemyUserRepository(UserRepository):
    """
    The Adapter.
    Translates domain calls into SQL via SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user: User) -> None:
        # We add to session, but DO NOT commit here.
        # Commits are the responsibility of the Unit of Work.
        self.session.add(_to_record(user))

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserRecord).where(UserRecord.email == email)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        if record is None:
            return None
        return _to_domain(record)
