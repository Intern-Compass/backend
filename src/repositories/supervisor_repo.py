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
        await conn.refresh(supervisor)

        return user

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

    async def get_supervisor_details(self, conn: AsyncSession, supervisor_id: str):
        stmt: Select = (
            select(Supervisor)
            .where(self.table.id == uuid.UUID(supervisor_id))
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
