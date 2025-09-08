from typing import Annotated
from uuid import UUID, uuid4

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import logger
from src.models import User
from src.models.app_models import Intern, Skill
from src.repositories import SkillRepository
from src.schemas import InternInModel


class InternRepository:
    def __init__(
            self,
            skill_repo: Annotated[SkillRepository, Depends()]
    ):
        self.table = Intern
        self.skill_repo = skill_repo

    async def create_new_intern(
        self, conn: AsyncSession, new_intern: InternInModel
    ) -> User:
        user_id: UUID = uuid4()
        user: User = User(
            id=user_id,
            firstname=new_intern.firstname,
            lastname=new_intern.lastname,
            email=new_intern.email,
            phone_number=new_intern.phone_number,
            password=new_intern.password,
        )
        skill_list = [
            (await self.skill_repo.create_or_get_skill(conn=conn, skill_name=skill.name))
            for skill in new_intern.skills
        ]
        user.skills = skill_list
        logger.info(skill_list)

        conn.add(user)
        await conn.flush()

        intern: Intern = self.table(
            user_id=user_id,
            division_name=new_intern.department,
            bio=new_intern.bio,
            supervisor=None,  # Default
            start_date=new_intern.internship_start_date,
            end_date=new_intern.internship_end_date,
        )
        conn.add(intern)
        await conn.flush()

        return user
