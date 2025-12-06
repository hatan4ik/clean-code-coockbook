import pytest
from src.domain.models import User


def test_user_creation():
    """Test that a User object can be created with valid data."""
    user = User(username="testuser", email="test@example.com")
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.id is not None
    assert user.created_at is not None


def test_username_validator_accepts_valid_name():
    """Test that the username validator passes with a valid username."""
    user = User(username="good_user_123", email="test@example.com")
    assert user.username == "good_user_123"


def test_username_validator_rejects_invalid_name():
    """Test that the username validator raises a ValueError for an invalid username."""
    with pytest.raises(ValueError, match="Username must be alphanumeric"):
        User(username="invalid-user!", email="test@example.com")


def test_can_receive_email_for_active_user():
    """Test that an active user can receive emails."""
    user = User(username="test", email="test@example.com", is_active=True)
    assert user.can_receive_email() is True


def test_can_receive_email_for_inactive_user():
    """Test that an inactive user cannot receive emails."""
    user = User(username="test", email="test@example.com", is_active=False)
    assert user.can_receive_email() is False