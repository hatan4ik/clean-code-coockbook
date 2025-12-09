from typing import Protocol, Self, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.ports import UserRepository

class AbstractUnitOfWork(Protocol):
    """Unit of Work pattern for managing transactions."""
    users: UserRepository  # Abstract interface, not concrete implementation

    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, *args) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...

class SqlAlchemyUnitOfWork:
    """
    Manages the atomicity of the business transaction.
    Either everything happens, or nothing happens.
    """
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self.session_factory = session_factory

    async def __aenter__(self) -> Self:
        self.session: AsyncSession = self.session_factory()
        self.users = SqlAlchemyUserRepository(self.session)
        return self

    async def __aexit__(self, exc_type, *args):
        try:
            if exc_type:
                await self.rollback()
            elif self.session.in_transaction():
                await self.rollback()
        finally:
            await self.session.close()

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        await self.session.rollback()
