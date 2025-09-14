import uuid
from uuid import UUID, uuid4

from sqlalchemy import Select, select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from . import SkillRepository
from ..common import UserType
from ..models import User
from ..models.app_models import Supervisor, Intern
from ..schemas.supervisor_schemas import SupervisorInModel
from ..utils import normalize_string


class SupervisorRepository:
    def __init__(self):
        self.table = Supervisor

    async def create_new_supervisor(
        self, conn: AsyncSession, new_supervisor: SupervisorInModel, user: User
    ):
        supervisor: Supervisor = self.table(
            position=new_supervisor.position,
        )

        user.supervisor = supervisor

        conn.add(user)
        await conn.flush()
        await conn.refresh(user)

        return user

    async def get_supervisors_by_ids(self, conn, ids: list[str]) -> list[Supervisor]:
        stmt = select(self.table).where(Supervisor.id.in_(ids)).options(
                selectinload(Supervisor.user).selectinload(User.skills)
            )
        result = await conn.execute(stmt)
        return result.scalars().all()

    async def assign_interns_to_supervisor(
        self, supervisor_id: id, conn: AsyncSession, interns_to_assign: list[Intern]
    ):
        stmt: Select = (
            select(self.table)
            .where(Supervisor.id == uuid.UUID(supervisor_id))
            .options(selectinload(Supervisor.interns))
        )
        supervisor: Supervisor = (await conn.execute(stmt)).scalar_one()

        supervisor.interns.extend(interns_to_assign)
        await conn.flush()

        return interns_to_assign

    async def get_supervisor_details(self, conn: AsyncSession, supervisor_id: UUID):
        stmt: Select = (
            select(self.table)
            .where(self.table.id == supervisor_id)
            .options(
                selectinload(Supervisor.user),
                selectinload(Supervisor.user).selectinload(User.skills),
                selectinload(Supervisor.interns),
                selectinload(Supervisor.interns).selectinload(Intern.user),
            )
        )

        result: Result = await conn.execute(stmt)
        return result.scalar_one()

    async def get_supervisors_details(self, conn):
        stmt: Select = select(self.table).options(
            selectinload(Supervisor.interns),
            selectinload(Supervisor.user),
            selectinload(Supervisor.user).selectinload(User.skills),
            selectinload(Supervisor.user).selectinload(User.department),
        )

        result: Result = await conn.execute(stmt)
        return result.scalars().all()

    async def get_supervisor_by_intern_user_id(self, conn: AsyncSession, intern_user_id: UUID) -> Supervisor | None:
        stmt = (
            select(self.table)
            .join(Intern, Intern.supervisor_id == self.table.id)
            .where(Intern.user_id == intern_user_id)
        )
        result = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def get_supervisor_by_intern_id(self, conn: AsyncSession, intern_id: UUID) -> Supervisor | None:
        stmt = (
            select(self.table)
            .where(Intern.id == intern_id)
            .options(selectinload(Intern.supervisor).selectinload(Supervisor.user))
        )
        result = await conn.execute(stmt)
        return result.scalar_one_or_none()
