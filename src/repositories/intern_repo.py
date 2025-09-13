import uuid

from typing import Annotated

import sqlalchemy.exc
from fastapi.params import Depends
from sqlalchemy import Select, select, Result, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.app_models import Intern, User, Supervisor
from ..repositories import SkillRepository
from ..schemas.intern_schemas import InternInModel
from ..schemas.user_schemas import UserType
from ..utils import normalize_string


class InternRepository:
    def __init__(self):
        self.table = Intern

    async def create_new_intern(
        self,
        conn: AsyncSession,
        new_intern: InternInModel,
        user: User,
    ) -> User:
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
            .options(
                selectinload(Intern.user),
                selectinload(Intern.user).selectinload(User.skills),
                selectinload(Intern.user).selectinload(User.department),
            )
        )
        result: Result = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def get_intern_by_user_id(self, conn: AsyncSession, user_id: uuid.UUID):
        stmt = (
            select(self.table)
            .join(User, User.id == self.table.user_id)
            .where(User.id == user_id)
        )
        result = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def get_interns(self, conn):
        stmt: Select = select(self.table).options(
            selectinload(Intern.user),
            selectinload(Intern.user).selectinload(User.skills),
            selectinload(Intern.user).selectinload(User.department),
        )
        result: Result = await conn.execute(stmt)

        return result.scalars().all()

    async def get_unmatched_interns(self, conn: AsyncSession):
        stmt: Select = (
            select(self.table)
            .where(Intern.supervisor_id == None)
            .options(
                selectinload(Intern.user).selectinload(User.skills),
                selectinload(Intern.user).selectinload(User.department),
            )
        )

        result: Result = await conn.execute(stmt)

        return result.scalars().all()

    async def assign_supervisor_to_intern(
        self, conn: AsyncSession, supervisor_id: str, intern_id: str
    ):
        intern_select: Select = (
            select(self.table)
            .where(
                and_(Intern.id == uuid.UUID(intern_id), Intern.supervisor_id == None)
            )
            .options(
                selectinload(Intern.user).selectinload(User.skills),
                selectinload(Intern.user).selectinload(User.department),
            )
        )

        supervisor_select: Select = select(Supervisor).where(
            Supervisor.id == uuid.UUID(supervisor_id)
        )

        try:
            intern_result: Intern = (await conn.execute(intern_select)).scalar_one()
        except sqlalchemy.exc.NoResultFound:
            raise ValueError("Intern does not exist")

        supervisor_result = (await conn.execute(supervisor_select)).scalar_one()
        intern_result.supervisor = supervisor_result

        await conn.flush()

        return intern_result
