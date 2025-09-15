from typing import AsyncGenerator
import pytest
from unittest.mock import AsyncMock
from fastapi import BackgroundTasks

from src.repositories.general_user_repo import UserRepository
from src.repositories.intern_repo import InternRepository
from src.repositories.skill_repo import SkillRepository
from src.repositories.supervisor_repo import SupervisorRepository
from src.repositories.verification_code_repo import VerificationCodeRepository
from src.services.auth_service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager


@asynccontextmanager
async def mock_async_context_manager() -> AsyncGenerator[None, None]:
    try:
        yield None
    finally:
        pass


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock(spec=AsyncSession)
    session.begin = mock_async_context_manager
    return session


@pytest.fixture
def mock_user_repo() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def mock_intern_repo() -> AsyncMock:
    return AsyncMock(spec=InternRepository)


@pytest.fixture
def mock_supervisor_repo() -> AsyncMock:
    return AsyncMock(spec=SupervisorRepository)


@pytest.fixture
def mock_code_repo() -> AsyncMock:
    return AsyncMock(spec=VerificationCodeRepository)


@pytest.fixture
def mock_skill_repo() -> AsyncMock:
    return AsyncMock(spec=SkillRepository)


@pytest.fixture
def mock_background_tasks() -> AsyncMock:
    return AsyncMock(spec=BackgroundTasks)


@pytest.fixture
def auth_service(
    mock_session: AsyncMock,
    mock_user_repo: AsyncMock,
    mock_intern_repo: AsyncMock,
    mock_supervisor_repo: AsyncMock,
    mock_code_repo: AsyncMock,
    mock_skill_repo: AsyncMock,
    mock_background_tasks: AsyncMock,
) -> AuthService:
    return AuthService(
        session=mock_session,
        user_repo=mock_user_repo,
        intern_repo=mock_intern_repo,
        supervisor_repo=mock_supervisor_repo,
        code_repo=mock_code_repo,
        skill_repo=mock_skill_repo,
        background_task=mock_background_tasks,
    )
