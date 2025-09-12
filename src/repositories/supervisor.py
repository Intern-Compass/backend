from typing import Annotated
from uuid import UUID

from sqlalchemy import select

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.app_models import Intern, Supervisor
from src.repositories.intern_repository import InternRepository


class SupervisorRepository:
    def __init__(
        self,
        intern: Annotated[InternRepository, Depends()]
    ):
        self.table = Supervisor
        self.intern_repo = intern

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
            .join(Intern, Intern.supervisor_id == self.table.id)
            .where(Intern.id == intern_id)
        )
        result = await conn.execute(stmt)
        return result.scalar_one_or_none()
