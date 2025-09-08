from uuid import UUID

from sqlalchemy import select, Select, Result, Delete, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.app_models import VerificationCode


class VerificationCodeRepository:
    def __init__(self):
        self.table = VerificationCode

    async def create_code(self, conn: AsyncSession, user_id: UUID, code: str):
        verification_code: VerificationCode = VerificationCode(
            user_id=user_id, value=code
        )
        conn.add(verification_code)
        await conn.flush()
        await conn.refresh(verification_code)

        return verification_code

    async def get_code(self, conn: AsyncSession, value: str):
        stmt: Select = select(self.table).where(self.table.value == value)
        result: Result = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def get_code_by_user_id(self, conn: AsyncSession, user_id: UUID):
        stmt: Select = select(self.table).where(self.table.user_id == user_id)
        result: Result = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_code_with_user_id(
        self, conn: AsyncSession, user_id: UUID, value: str
    ):
        stmt = insert(self.table).values(user_id=user_id, value=value)
        stmt = stmt.on_conflict_do_update(
            index_elements=["user_id"],  # column with unique constraint
            set_={"value": value},
        )
        await conn.execute(stmt)

    async def delete_code(self, conn: AsyncSession, value: str) -> None:
        stmt: Delete = delete(self.table).where(self.table.value == value)
        await conn.execute(stmt)
