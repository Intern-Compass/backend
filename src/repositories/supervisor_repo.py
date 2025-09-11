import uuid
from uuid import UUID, uuid4

from sqlalchemy import Select, select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..common import UserType
from ..models import User
from ..models.app_models import Supervisor, Intern
from ..schemas.supervisor_schemas import SupervisorInModel
from ..utils import normalize_email


class SupervisorRepository:
    def __init__(self):
        self.table = Supervisor

    async def create_new_supervisor(
        self, conn: AsyncSession, new_supervisor: SupervisorInModel
    ):
        user_id: UUID = uuid4()
        user: User = User(
            id=user_id,
            firstname=new_supervisor.firstname,
            lastname=new_supervisor.lastname,
            email=new_supervisor.email,
            normalized_email=normalize_email(new_supervisor.email),
            phone_number=new_supervisor.phone_number,
            password=new_supervisor.password,
            date_of_birth=new_supervisor.date_of_birth,
            work_location=new_supervisor.work_location,
            type=UserType.SUPERVISOR,
            department_id=new_supervisor.department.value,
        )

        supervisor: Supervisor = self.table(
            user_id=user_id,
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
            .options(selectinload(Supervisor.interns))
        )

        result: Result = await conn.execute(stmt)
        return result.scalar_one()
