"""
This module will handle:
    - Creation of accounts for intern
    - Viewing supervisor intern was assigned to
    - Viewing tasks assigned by the supervisor
    Anything else the intern_auth router might need
"""
from typing import Annotated
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.params import Depends
from fastapi import HTTPException

from src.models.app_models import Project
from src.repositories.intern_repository import InternRepository
from src.repositories.project_repo import ProjectRepository
from src.repositories.supervisor import SupervisorRepository
from src.repositories.task_repo import TaskRepository
from ..db import get_db_session
from ..schemas.intern_schemas import ISupervisor
from ..schemas.task_schemas import TaskOutModel


class InternService:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        task: Annotated[TaskRepository, Depends()],
        intern: Annotated[InternRepository, Depends()],
        project: Annotated[ProjectRepository, Depends()],
        supervisor: Annotated[SupervisorRepository, Depends()]
    ) -> None:
        self.session = session
        self.task_repo = task
        self.intern_repo = intern
        self.supervisor_repo = supervisor
        self.project_repo = project

    async def get_supervisor(self, user_id: uuid.UUID) -> ISupervisor:
        async with self.session.begin():
            intern = await self.intern_repo.get_intern_by_user_id(self.session, user_id)
            if not intern:
                raise HTTPException(status_code=404, detail="Intern not found")
            return await self.supervisor_repo.get_supervisor_by_intern_id(self.session, intern.id)

    async def get_tasks(self, user_id: uuid.UUID) -> list[TaskOutModel]:
        async with self.session.begin():
            intern = await self.intern_repo.get_intern_by_user_id(self.session, user_id)
            if not intern:
                raise HTTPException(status_code=404, detail="Intern not found")
            return await self.task_repo.get_all_tasks_by_intern_id(self.session, intern.id)

    async def get_projects(self, user_id: uuid.UUID) -> list[Project]:
        async with self.session.begin():
            intern = await self.intern_repo.get_intern_by_user_id(self.session, user_id)
            if not intern:
                raise HTTPException(status_code=404, detail="Intern not found")
            return await self.project_repo.get_all_projects_by_intern_id(self.session, intern.id)
