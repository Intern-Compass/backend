from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.logger import logger
from src.matching import matcher
from src.models.app_models import Supervisor, Intern
from src.repositories.intern_repo import InternRepository
from src.repositories.supervisor_repo import SupervisorRepository


class MatchingService:
    def __init__(
        self,
        intern_repo: Annotated[InternRepository, Depends()],
        supervisor_repo: Annotated[SupervisorRepository, Depends()],
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ):
        self.intern_repo = intern_repo
        self.supervisor_repo = supervisor_repo
        self.session = session

    async def perform_bulk_matching(self):
        async with self.session.begin():
            supervisors: list[
                Supervisor
            ] = await self.supervisor_repo.get_supervisors_details(conn=self.session)
            unmatched_interns: list[
                Intern
            ] = await self.intern_repo.get_unmatched_interns(conn=self.session)

            matches: dict = await matcher(supervisors, unmatched_interns)

        for department, department_match in matches.items():
            logger.info(f"Matching for department: {department}")

            for supervisor, intern_list in department_match.items():
                for intern in intern_list:
                    try:
                        await self.intern_repo.assign_supervisor_to_intern(
                            conn=self.session,
                            supervisor_id=supervisor,
                            intern_id=intern,
                        )
                    except ValueError:
                        logger.info(f"Inern {intern} does not exist")
                        continue
