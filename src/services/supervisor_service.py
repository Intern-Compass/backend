from typing import Annotated
from uuid import UUID

from fastapi import BackgroundTasks
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..common import DepartmentEnum
from ..db import get_db_session
from ..models.app_models import Intern, Supervisor
from ..repositories.intern_repo import InternRepository
from ..repositories.supervisor_repo import SupervisorRepository
from ..schemas.intern_schemas import InternOutModel, BasicUserDetails
from ..schemas.supervisor_schemas import SupervisorOutModel


class SupervisorService:
    def __init__(
        self,
        supervisor_repo: Annotated[SupervisorRepository, Depends()],
        intern_repo: Annotated[InternRepository, Depends()],
        background_tasks: BackgroundTasks,
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ):
        self.supervisor_repo = supervisor_repo
        self.background_tasks = background_tasks
        self.session = session
        self.intern_repo = intern_repo

    async def get_interns(self, supervisor_id: UUID):
        async with self.session.begin():
            interns: list[Intern] = await self.intern_repo.get_interns_for_supervisor(
                conn=self.session, supervisor_id=supervisor_id
            )

        return [InternOutModel.from_model(intern) for intern in interns]

    async def get_supervisors(self):
        async with self.session.begin():
            supervisors: list[
                Supervisor
            ] = await self.supervisor_repo.get_supervisors_details(conn=self.session)

        return [SupervisorOutModel.from_model(supervisor) for supervisor in supervisors]
