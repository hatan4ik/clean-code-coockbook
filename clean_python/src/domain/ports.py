from typing import Protocol, Optional
from uuid import UUID
from .models import User

class UserRepository(Protocol):
    """
    The Port (Interface).
    The domain says: "I need a way to save users, I don't care how."
    """
    async def add(self, user: User) -> None:
        ...

    async def get_by_email(self, email: str) -> Optional[User]:
        ...
