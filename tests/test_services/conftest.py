import pytest
from unittest.mock import AsyncMock
from fastapi import BackgroundTasks

from src.services.auth_service import AuthService

from contextlib import asynccontextmanager


@asynccontextmanager
async def mock_async_context_manager():
    try:
        yield None
    finally:
        pass


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.begin = mock_async_context_manager
    return session


@pytest.fixture
def mock_user_repo():
    return AsyncMock()


@pytest.fixture
def mock_intern_repo():
    return AsyncMock()


@pytest.fixture
def mock_code_repo():
    return AsyncMock()


@pytest.fixture
def mock_background_tasks():
    return AsyncMock(spec=BackgroundTasks)


@pytest.fixture
def auth_service(
    mock_session,
    mock_user_repo,
    mock_intern_repo,
    mock_code_repo,
    mock_background_tasks,
):
    return AuthService(
        session=mock_session,
        user_repo=mock_user_repo,
        intern_repo=mock_intern_repo,
        code_repo=mock_code_repo,
        background_task=mock_background_tasks,
    )
