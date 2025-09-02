from sqlalchemy import Select, select, Result

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.intern_model import User
from src.repositories.base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_user_by_email(self, conn: AsyncSession, email: str):
        stmt: Select = select(User).where(User.c.email == email)
        result: Result = await conn.execute(stmt)
        return result.fetchone()
