from typing import Annotated

from fastapi import BackgroundTasks, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from ..db import get_db_session
from ..models.app_models import Intern, Supervisor
from ..repositories.intern_repo import InternRepository
from ..repositories.supervisor_repo import SupervisorRepository
from ..schemas.intern_schemas import InternOutModel




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

    async def get_interns(self, supervisor_id: str):
        # TODO: IMPORTANT Fix the loading of relationships
        async with self.session.begin():
            supervisor: Supervisor = (
                await self.supervisor_repo.get_supervisor_details(
                    conn=self.session, supervisor_id=supervisor_id
                )
            )

        return [InternOutModel.from_user(intern.user) for intern in supervisor.interns]

    async def assign_intern_to_supervisor(self, supervisor_id: str, intern_id: str):
        async with self.session.begin():
            existing_intern: Intern | None = await self.intern_repo.get_intern_by_id(
                conn=self.session, intern_id=intern_id
            )

            if not existing_intern:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND, detail="Intern not found"
                )

            if existing_intern.supervisor_id:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND,
                    detail="Intern already assigned to supervisor",
                )

            await self.supervisor_repo.assign_interns_to_supervisor(
                conn=self.session,
                supervisor_id=supervisor_id,
                interns_to_assign=[existing_intern],
            )

        print({"detail": f"{existing_intern.user.email} has been assigned a supervisor"})

    async def get_supervisor(self, supervisor_id: str):
        async with self.session.begin():
            supervisor: Supervisor = (
                await self.supervisor_repo.get_supervisor_details(
                    conn=self.session, supervisor_id=supervisor_id
                )
            )

        return supervisor

    async def get_supervisors(self):
        async with self.session.begin():
            supervisors: list[Supervisor] = await self.supervisor_repo.get_supervisors_details(conn=self.session)

        return supervisors



