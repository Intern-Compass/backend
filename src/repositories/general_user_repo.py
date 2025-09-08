from os import name
from uuid import UUID

from sqlalchemy import Select, select, Result, update, delete, or_, Update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.app_models import User, Skill
from src.schemas import UserInModel




class UserRepository:
    def __init__(self):
        self.table = User

    async def get_user_by_email_or_phone(
        self,
        conn: AsyncSession,
        email: str | None = None,
        phone_number: str | None = None,
    ):
        if email is None and phone_number is None:
            raise ValueError("Either email or phone_number must be supplied.")

        stmt: Select = select(self.table).where(
            or_(self.table.email == email, self.table.phone_number == phone_number),
        )
        result: Result = await conn.execute(stmt)
        return result.scalars().first()

    async def create_new_user(self, new_user: UserInModel, conn: AsyncSession) -> User:
        user: User = self.table(
            firstname=new_user.firstname,
            lastname=new_user.lastname,
            phone_number=new_user.phone_number,
            email=new_user.email,
            password=new_user.password,
        )
        user.skills = [Skill(name=skill.name) for skill in new_user.skills]

        conn.add(user)
        await conn.flush()
        await conn.refresh(user)

        return user

    async def get_by_id(self, conn: AsyncSession, id_value: str) -> User | None:
        stmt = select(self.table).where(self.table.id == id_value)
        result = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, conn: AsyncSession):
        stmt = select(self.table)
        result = await conn.execute(stmt)
        return result.fetchall()

    async def update(
        self, conn: AsyncSession, user_id: UUID, values: dict
    ) -> User | None:
        stmt: Update[User] = (
            update(self.table)
            .where(self.table.id == user_id)
            .values(**values)
            .returning(self.table)
        )
        result: Result[tuple[User]] = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, conn: AsyncSession, id_value: str) -> None:
        stmt = delete(self.table).where(self.table.id == id_value)
        await conn.execute(stmt)
