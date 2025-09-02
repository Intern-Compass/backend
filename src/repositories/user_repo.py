from sqlalchemy import Select, select, Result, insert, update, delete

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.app_models import User
from src.repositories.base_repo import BaseRepository
from src.schemas import UserInModel


class UserRepository:
    def __init__(self):
        self.table = User

    async def get_user_by_email(self, conn: AsyncSession, email: str):
        stmt: Select = select(self.table).where(
            self.table.email == email
        )
        result: Result = await conn.execute(stmt)
        return result.fetchone()

    async def create_new_user(self, new_user: UserInModel, conn: AsyncSession):
        stmt = insert(self.table).values(**new_user.model_dump()).returning(self.table)
        result = await conn.execute(stmt)
        return result.fetchone()

    async def get_by_id(self, conn: AsyncSession, id_value: str):
        stmt = select(self.table).where(self.table.id == id_value)
        result = await conn.execute(stmt)
        return result.fetchone()

    async def list_all(self, conn: AsyncSession):
        stmt = select(self.table)
        result = await conn.execute(stmt)
        return result.fetchall()

    async def update(self, conn: AsyncSession, id_value: str, values: dict):
        stmt = (
            update(self.table)
            .where(self.table.id == id_value)
            .values(**values)
            .returning(self.table)
        )
        result = await conn.execute(stmt)
        return result.fetchone()

    async def delete(self, conn: AsyncSession, id_value: str) -> None:
        stmt = delete(self.table).where(self.table.id == id_value)
        await conn.execute(stmt)