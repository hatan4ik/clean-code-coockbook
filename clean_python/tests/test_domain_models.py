import pytest
from src.domain.models import User

def test_user_creation():
    """
    Tests that a User can be created with valid data.
    """
    user = User(username="testuser", email="test@example.com")
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True

def test_username_validation_success():
    """
    Tests that usernames with valid characters are accepted.
    """
    user = User(username="valid_user_123", email="test@example.com")
    assert user.username == "valid_user_123"

def test_username_validation_fails():
    """
    Tests that the username validator raises a ValueError for invalid characters.
    """
    with pytest.raises(ValueError, match="Username must be alphanumeric"):
        User(username="invalid-user!", email="test@example.com")

def test_can_receive_email():
    """
    Tests the business logic for can_receive_email.
    """
    active_user = User(username="active", email="a@a.com", is_active=True)
    inactive_user = User(username="inactive", email="b@b.com", is_active=False)

    assert active_user.can_receive_email() is True
    assert inactive_user.can_receive_email() is False
