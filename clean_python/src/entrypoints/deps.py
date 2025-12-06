from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config import settings
from src.service_layer.unit_of_work import SqlAlchemyUnitOfWork

# Wiring the infrastructure
engine = create_async_engine(settings.database_url, echo=settings.echo_sql)
session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)


def get_uow() -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session_factory)
