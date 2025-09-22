from collections import defaultdict
from typing import Annotated, TYPE_CHECKING
from uuid import UUID

from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT

from ..common import DepartmentEnum
from ..db import get_db_session
from ..logger import logger
from ..matching import matcher
from ..models.app_models import Supervisor, Intern
from ..repositories.intern_repo import InternRepository
from ..repositories.supervisor_repo import SupervisorRepository
from ..schemas.intern_schemas import BasicUserDetails, InternOutModel

if TYPE_CHECKING:
    from ..common import InternMatchDetail

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

    async def display_matches(self):
        async with self.session.begin():
            supervisors_from_db: list[Supervisor] = \
                await self.supervisor_repo.get_supervisors_details(conn=self.session)

            unmatched_interns_from_db: list[Intern] = \
                await self.intern_repo.get_unmatched_interns(conn=self.session)

            supervisor_map = {str(s.id): s for s in supervisors_from_db}
            intern_map = {str(i.id): i for i in unmatched_interns_from_db}

            match_details: dict[
                str, list[tuple[BasicUserDetails, list[dict]]]
            ] = defaultdict(list)

            matches: dict = matcher(supervisors_from_db, unmatched_interns_from_db)

            for department, department_matches in matches.items():
                for supervisor_id, intern_matches in department_matches.items():
                    supervisor_details = supervisor_map[supervisor_id]

                    formatted_supervisor: BasicUserDetails = BasicUserDetails(
                        firstname=supervisor_details.user.firstname,
                        lastname=supervisor_details.user.lastname,
                        department=DepartmentEnum(supervisor_details.user.department_id),
                        email=supervisor_details.user.email,
                        phone_number=supervisor_details.user.phone_number,
                        skills= [skill.name for skill in supervisor_details.user.skills]
                    )

                    formatted_intern_list: list[dict] = [
                        {
                            "firstname": intern_map[intern.intern_id].user.firstname,
                            "lastname": intern_map[intern.intern_id].user.lastname,
                            "department": DepartmentEnum(intern_map[intern.intern_id].user.department_id),
                            "email": intern_map[intern.intern_id].user.email,
                            "phone_number": intern_map[intern.intern_id].user.phone_number,
                            "skills": [
                                        skill.name
                                        for skill in intern_map[intern.intern_id].user.skills
                                    ],
                            "similarity": f"{(intern.similarity * 100):.2f}%"
                        }
                        for intern in intern_matches # type: InternMatchDetail
                    ]

                    match_details[department].append(
                        (formatted_supervisor, formatted_intern_list)
                    )

            return match_details

    async def perform_bulk_matching(self):
        async with self.session.begin():
            supervisors: list[
                Supervisor
            ] = await self.supervisor_repo.get_supervisors_details(conn=self.session)
            unmatched_interns: list[
                Intern
            ] = await self.intern_repo.get_unmatched_interns(conn=self.session)

            matches: dict = matcher(supervisors, unmatched_interns)

            for department, department_match in matches.items():
                logger.info(f"Matching for department: {department}")

                for supervisor_id, intern_matches in department_match.items():
                    for intern in intern_matches: # type: InternMatchDetail
                        try:
                            await self.intern_repo.assign_supervisor_to_intern(
                                conn=self.session,
                                supervisor_id=UUID(supervisor_id),
                                intern_id=UUID(intern.intern_id),
                            )
                        except ValueError:
                            logger.info(f"Intern {intern.intern_id} does not exist")
                            continue

        return {"detail": "Matching performed successfully"}

    async def manually_match_supervisor_to_intern(self, supervisor_id: UUID, intern_id: UUID):
        async with self.session.begin():
            intern: Intern = await self.intern_repo.get_intern_by_id(
                conn=self.session,
                intern_id=intern_id
            )

            if not intern:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Intern not found")

            if sup_id := intern.supervisor_id:
                if sup_id == supervisor_id:
                    raise HTTPException(
                        status_code=HTTP_409_CONFLICT,
                        detail= "This supervisor has already been assigned to this intern"
                    )

                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Intern has already been matched to a supervisor. "
                           "Unmatch the existing supervisor before matching a new one"
                )

            assigned_interns: list[Intern] =  await self.supervisor_repo.assign_interns_to_supervisor(
                supervisor_id=supervisor_id,
                interns_to_assign=[intern],
                conn=self.session
            )

            return [InternOutModel.from_model(intern) for intern in assigned_interns]

    async def unmatch_supervisor_from_intern(self, intern_id: UUID):
        async with self.session.begin():
            intern: Intern = await self.intern_repo.get_intern_by_id(
                conn=self.session,
                intern_id=intern_id
            )

            if not intern.supervisor_id:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Intern has not been assigned a supervisor yet"
                )

            await self.intern_repo.unassign_supervisor(
                conn=self.session,
                intern_id=intern_id
            )

            return {"detail": "Successfully unmatched intern from supervisor"}