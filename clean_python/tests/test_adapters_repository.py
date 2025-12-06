import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.adapters.orm import Base, UserRecord
from src.domain.models import User
from src.service_layer.unit_of_work import SqlAlchemyUnitOfWork


@pytest_asyncio.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield factory
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_sqlalchemy_repo_persists_user(session_factory):
    uow = SqlAlchemyUnitOfWork(session_factory)
    async with uow:
        await uow.users.add(User(username="alice", email="alice@example.com"))
        await uow.commit()

    async with session_factory() as session:
        result = await session.execute(select(UserRecord).where(UserRecord.email == "alice@example.com"))
        record = result.scalar_one_or_none()
        assert record is not None
        assert record.username == "alice"
        assert record.is_active is True


@pytest.mark.asyncio
async def test_uow_rolls_back_on_error(session_factory):
    uow = SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(RuntimeError):
        async with uow:
            await uow.users.add(User(username="bob", email="bob@example.com"))
            raise RuntimeError("boom")

    async with session_factory() as session:
        result = await session.execute(select(UserRecord).where(UserRecord.email == "bob@example.com"))
        assert result.scalar_one_or_none() is None
