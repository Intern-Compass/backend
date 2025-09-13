"""
This module will handle:
    - Creation of accounts for intern
    - Viewing supervisor intern was assigned to
    - Viewing tasks assigned by the supervisor
    Anything else the intern_auth router might need
"""
import uuid
from typing import Annotated

from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db_session
from ..models.app_models import Intern, Project, Supervisor
from ..repositories.intern_repo import InternRepository
from ..repositories.project_repo import ProjectRepository
from ..repositories.supervisor_repo import SupervisorRepository
from ..repositories.task_repo import TaskRepository
from ..schemas.intern_schemas import ISupervisor
from ..schemas.supervisor_schemas import SupervisorOutModel
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

    async def get_supervisor_by_intern_user_id(self, user_id: uuid.UUID) -> ISupervisor:
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

    async def get_intern(self, intern_id: str):
        async with self.session.begin():
            intern = await self.intern_repo.get_intern_by_id(
                conn=self.session, intern_id=intern_id
            )

        return intern

    async def get_interns(self):
        async with self.session.begin():
            interns: list[Intern] = await self.intern_repo.get_interns(
                conn=self.session
            )

        return interns

    async def get_unmatched_interns(self):
        async with self.session.begin():
            unmatched_interns: list[
                Intern
            ] = await self.intern_repo.get_unmatched_interns(conn=self.session)

        return unmatched_interns

    async def get_intern_supervisor(self, intern_id: str):
        async with self.session.begin():
            intern: Intern = await self.intern_repo.get_intern_by_id(
                conn=self.session, intern_id=intern_id
            )
            supervisor_id = intern.supervisor_id

            supervisor: Supervisor = await self.supervisor_repo.get_supervisor_details(
                conn=self.session, supervisor_id=str(supervisor_id)
            )

            return SupervisorOutModel.from_supervisor(supervisor.user)
