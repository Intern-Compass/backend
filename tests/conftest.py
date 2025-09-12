"""
Global test configuration and fixtures.
"""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.main import app
from src.settings import settings
from src.models.app_models import Base
from src.db import get_db_session

# Use a separate database for testing
TEST_DB_URL = f"{settings.DB_URL}_test"  # Ensure there is a DB in the DB server with this name. This should be okay for local dev, but CI workflow should start fresh Docker containers for each test run.

# Create a new async engine for the test database
engine = create_async_engine(TEST_DB_URL, echo=False)

# Create a new sessionmaker for the test database
TestingAsyncSessionLocal = async_sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)

# --- Database Fixtures ---


@pytest_asyncio.fixture(scope="session")  # Issues with scoping fixtures
async def manage_db_schema() -> AsyncGenerator[None, None]:
    """
    Fixture to create and drop the test database schema for the entire test session.
    """
    async with engine.begin() as conn:
        # Create all tables defined in app_models (from Base.metadata)
        await conn.run_sync(Base.metadata.create_all)

    yield  # Tests run here

    async with engine.begin() as conn:
        # Drop all tables after the test session is complete
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")  # Issues with scoping fixtures
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture to provide a clean database session for each test function.
    """
    async with TestingAsyncSessionLocal() as session:
        yield session


# --- Application Fixtures ---
"""
@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    # Fixture to create an AsyncClient for making API requests.
    # This also handles overriding the database dependency.

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db

    # Create and yield the test client
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clean up the override after the test
    app.dependency_overrides.clear()
"""
