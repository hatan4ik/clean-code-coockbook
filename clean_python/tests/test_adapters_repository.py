from __future__ import annotations

from typing import TYPE_CHECKING
import pytest

from src.adapters.orm import SqlAlchemyUserRepository
from src.domain.models import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


pytestmark = pytest.mark.asyncio


async def test_repository_can_add_and_get_user(test_db_session: AsyncSession):
    """
    Test that the repository can add a user to the database and retrieve it.
    """
    repo = SqlAlchemyUserRepository(test_db_session)
    user = User(username="testuser", email="test@example.com")

    # Add user and commit
    await repo.add(user)
    await test_db_session.commit()

    # Retrieve user
    retrieved_user = await repo.get_by_email("test@example.com")

    assert retrieved_user is not None
    assert retrieved_user.username == "testuser"
    assert retrieved_user.email == "test@example.com"
    assert retrieved_user.id == user.id


async def test_repository_get_returns_none_for_nonexistent_user(
    test_db_session: AsyncSession,
):
    """
    Test that the repository returns None when trying to get a user that does not exist.
    """
    repo = SqlAlchemyUserRepository(test_db_session)
    retrieved_user = await repo.get_by_email("nonexistent@example.com")
    assert retrieved_user is None