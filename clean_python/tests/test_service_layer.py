from typing import List, Optional
import pytest
from src.domain.models import User
from src.domain.ports import UserRepository
from src.service_layer.unit_of_work import AbstractUnitOfWork
from src.service_layer import handlers

# Fakes (for testing without real infrastructure)

class FakeUserRepository(UserRepository):
    """
    In-memory fake repository for testing.
    """
    def __init__(self, users: List[User]):
        self._users = list(users)

    async def add(self, user: User) -> None:
        self._users.append(user)

    async def get_by_email(self, email: str) -> Optional[User]:
        return next((u for u in self._users if u.email == email), None)
    
    def list(self) -> List[User]:
        return list(self._users)

class FakeUnitOfWork(AbstractUnitOfWork):
    """
    In-memory fake Unit of Work.
    """
    def __init__(self):
        self.users = FakeUserRepository([])
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def commit(self):
        self.committed = True

    async def rollback(self):
        pass


# Tests

@pytest.mark.asyncio
async def test_register_user_service_success():
    """
    Tests that the register_user_service creates a user correctly.
    """
    uow = FakeUnitOfWork()
    
    # Execute the service
    user = await handlers.register_user_service(
        username="testuser",
        email="test@example.com",
        uow=uow,
    )

    # Assertions
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    
    # Check that it was saved to the fake repo
    saved_user = await uow.users.get_by_email("test@example.com")
    assert saved_user is not None
    assert saved_user.username == "testuser"

    # Check that the transaction was committed
    assert uow.committed is True

@pytest.mark.asyncio
async def test_register_user_service_already_exists():
    """
    Tests that the service raises a ValueError if the user's email already exists.
    """
    # Seed the repo with an existing user
    existing_user = User(username="existing", email="exists@example.com")
    uow = FakeUnitOfWork()
    await uow.users.add(existing_user)

    # Expect an exception
    with pytest.raises(ValueError, match="User exists@example.com already exists"):
        await handlers.register_user_service(
            username="newuser",
            email="exists@example.com", # Same email
            uow=uow,
        )
    
    # Check that the transaction was NOT committed
    assert uow.committed is False
