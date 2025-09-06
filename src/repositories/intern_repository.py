from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.models.app_models import Intern
from src.schemas import InternInModel


class InternRepository:
    def __init__(self):
        self.table = Intern

    async def create_new_intern(self, conn: AsyncSession, new_intern: InternInModel) -> User:
        user_id: UUID = uuid4()
        user: User = User(
            id=user_id,
            firstname=new_intern.firstname,
            lastname=new_intern.lastname,
            email=new_intern.email,
            phone_number=new_intern.phone_number,
            password=new_intern.password
        )
        conn.add(user)
        await conn.flush()

        intern: Intern = Intern(
            user_id=user_id,
            division_name=new_intern.department,
            bio=new_intern.bio,
            supervisor=None, #Default
            start_date=new_intern.internship_start_date,
            end_date=new_intern.internship_end_date,
        )
        conn.add(intern)
        await conn.flush()

        return user