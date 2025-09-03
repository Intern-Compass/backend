from sqlalchemy import MetaData, create_engine, Engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncEngine

from src.settings import settings

engine: AsyncEngine = create_async_engine(url=settings.DB_URL, echo=False)

SessionLocal = async_sessionmaker(bind=engine, autocommit=False, expire_on_commit=False)

async def get_db_session():
    async with SessionLocal() as session:
        yield session  # Automatically manages commit/rollback