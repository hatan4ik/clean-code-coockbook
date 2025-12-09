import pytest
from src.domain.models import User
from src.service_layer import handlers

pytestmark = pytest.mark.asyncio


async def test_register_user_service_happy_path(uow):
    """Test that a user can be successfully registered."""
    user = await handlers.register_user_service(
        "testuser", "test@example.com", uow
    )

    assert user.username == "testuser"
    assert user.email == "test@example.com"

    # Verify it was committed
    async with uow:
        retrieved_user = await uow.users.get_by_email("test@example.com")
        assert retrieved_user is not None
        assert retrieved_user.username == "testuser"


async def test_register_user_service_raises_error_if_user_exists(uow):
    """Test that registering a user with an existing email raises a ValueError."""
    # Pre-add a user
    async with uow:
        uow.users.add(User(username="existing", email="test@example.com"))
        await uow.commit()

    # Attempt to register the same user and expect an error
    with pytest.raises(ValueError, match="User already exists"):
        await handlers.register_user_service(
            "newuser", "test@example.com", uow
        )