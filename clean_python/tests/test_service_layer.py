from __future__ import annotations

from typing import TYPE_CHECKING
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


from src.domain.models import User
from src.service_layer import handlers
from src.service_layer.unit_of_work import SqlAlchemyUnitOfWork

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


pytestmark = pytest.mark.asyncio


async def test_register_user_service_happy_path():
    """Test that a user can be successfully registered."""
    # Use a separate engine/session factory for this test to ensure isolation
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    uow = SqlAlchemyUnitOfWork(session_factory)

    # We need to create the tables for the UoW to work
    # This would typically be handled by a migration tool like Alembic
    from src.adapters.orm import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


    # Run the service
    user = await handlers.register_user_service(
        "testuser", "test@example.com", uow
    )

    # Check the result
    assert user.username == "testuser"
    assert user.email == "test@example.com"

    # Verify it was committed
    async with uow:
        retrieved_user = await uow.users.get_by_email("test@example.com")
        assert retrieved_user is not None
        assert retrieved_user.username == "testuser"


async def test_register_user_service_raises_error_if_user_exists():
    """Test that registering a user with an existing email raises a ValueError."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    uow = SqlAlchemyUnitOfWork(session_factory)

    from src.adapters.orm import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Pre-add a user
    async with uow:
        await uow.users.add(User(username="existing", email="test@example.com"))
        await uow.commit()

    # Attempt to register the same user and expect an error
    with pytest.raises(ValueError, match="User test@example.com already exists"):
        await handlers.register_user_service(
            "newuser", "test@example.com", uow
        )