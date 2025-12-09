import asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.adapters.orm import Base
from src.service_layer.unit_of_work import SqlAlchemyUnitOfWork


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_engine():
    """Create in-memory database engine for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def uow(db_engine):
    """Provide Unit of Work for tests."""
    session_factory = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    return SqlAlchemyUnitOfWork(session_factory)
