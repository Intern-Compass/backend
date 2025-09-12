"""
This module will handle:
    - Creation of accounts for intern
    - Viewing supervisor intern was assigned to
    - Viewing tasks assigned by the supervisor
    Anything else the intern_auth router might need
"""

from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db_session
from ..models.app_models import Intern, Supervisor
from ..repositories.intern_repo import InternRepository
from ..repositories.supervisor_repo import SupervisorRepository
from ..schemas.supervisor_schemas import SupervisorOutModel


class InternService:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        intern_repo: Annotated[InternRepository, Depends()],
        supervisor_repo: Annotated[SupervisorRepository, Depends()],
    ):
        self.session = session
        self.intern_repo = intern_repo
        self.supervisor_repo = supervisor_repo

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
