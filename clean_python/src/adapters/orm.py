from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models import User
from src.domain.ports import UserRepository

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
        self.session.add(user)

    async def get_by_email(self, email: str) -> Optional[User]:
        # Using SQLAlchemy 2.0 style syntax
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
