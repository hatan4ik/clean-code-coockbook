from typing import Protocol, Optional
from uuid import UUID
from .models import User

class UserRepository(Protocol):
    """
    The Port (Interface).
    The domain says: "I need a way to save users, I don't care how."
    """
    def add(self, user: User) -> None:
        """Add user to session (synchronous operation)."""
        ...

    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email (async I/O operation)."""
        ...
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve user by ID (async I/O operation)."""
        ...
