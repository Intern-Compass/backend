import uuid

from typing import Annotated
from uuid import UUID, uuid4

from fastapi.params import Depends
from sqlalchemy import Select, select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.logger import logger
from src.models import User
from src.models.app_models import Intern
from src.repositories import SkillRepository
from src.schemas import InternInModel
from src.schemas.user_schemas import UserType
from src.utils import normalize_email


class InternRepository:
    def __init__(self, skill_repo: Annotated[SkillRepository, Depends()]):
        self.table = Intern
        self.skill_repo = skill_repo

    async def create_new_intern(
        self, conn: AsyncSession, new_intern: InternInModel
    ) -> User:
        user: User = User(
            firstname=new_intern.firstname,
            lastname=new_intern.lastname,
            email=new_intern.email,
            normalized_email=normalize_email(new_intern.email),
            phone_number=new_intern.phone_number,
            password=new_intern.password,
            date_of_birth=new_intern.date_of_birth,
            work_location=new_intern.work_location,
            type=UserType.INTERN,
            department_id=new_intern.department.value,
        )
        skill_list = [
            (
                await self.skill_repo.create_or_get_skill(
                    conn=conn, skill_name=skill.name
                )
            )
            for skill in new_intern.skills
        ]
        user.skills = skill_list

        intern: Intern = self.table(
            bio=new_intern.bio,
            school=new_intern.school,
            start_date=new_intern.internship_start_date,
            end_date=new_intern.internship_end_date,
        )
        user.intern = intern

        conn.add(user)
        await conn.flush()

        return user

    async def get_intern_by_id(self, conn: AsyncSession, intern_id: str):
        stmt: Select = (
            select(self.table)
            .where(self.table.id == uuid.UUID(intern_id))
            .options(selectinload(Intern.user))
        )
        result: Result = await conn.execute(stmt)

        return result.scalar_one_or_none()
