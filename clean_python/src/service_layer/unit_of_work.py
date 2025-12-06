from typing import Protocol, Self
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.orm import SqlAlchemyUserRepository

class AbstractUnitOfWork(Protocol):
    users: SqlAlchemyUserRepository

    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, *args) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...

class SqlAlchemyUnitOfWork:
    """
    Manages the atomicity of the business transaction.
    Either everything happens, or nothing happens.
    """
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self) -> Self:
        self.session: AsyncSession = self.session_factory()
        self.users = SqlAlchemyUserRepository(self.session)
        return self

    async def __aexit__(self, exc_type, *args):
        if exc_type:
            await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
