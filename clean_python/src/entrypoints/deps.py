# Wiring the infrastructure
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.service_layer.unit_of_work import SqlAlchemyUnitOfWork

# In real app, load from config.py
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/db"

engine = create_async_engine(DATABASE_URL, echo=True)
session_factory = async_sessionmaker(bind=engine)

def get_uow() -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session_factory)
