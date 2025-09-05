import logging
import uuid

from sqlalchemy import Select, select, Result, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.app_models import InternSkill, Skill, SupervisorSkill, User
from src.schemas import UserInModel
from src.schemas.user_schemas import SkillAttachReq, SkillCreate, SkilledUserLitral, UserAccountTypeEmun


logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self):
        self.table = User

    async def get_user_by_email(self, conn: AsyncSession, email: str):
        stmt: Select = select(self.table).where(
            self.table.email == email
        )
        result: Result = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def create_new_user(self, new_user: UserInModel, conn: AsyncSession):
        user: User = User(
            email = new_user.email,
            password = new_user.password
        )
        conn.add(user)
        await conn.commit()
        await conn.refresh(user)

        return user

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

    async def attach_skills_to_user(
        self, conn: AsyncSession, user_id: uuid.UUID,
        user_type: SkilledUserLitral, skill_data: list[SkillAttachReq]
    ):
        # NOTE: this doesn't check for duplicates
        # TODO: implement duplicate handling
        if user_type == UserAccountTypeEmun.intern.value:
            objs = [
                InternSkill(
                    intern_id=user_id,
                    skill_id=skill.id, note=skill.note
                ) for skill in skill_data
            ]
        elif user_type == UserAccountTypeEmun.supervisor.value:
            objs = [
                SupervisorSkill(
                    supervisor_id=user_id,
                    skill_id=skill.id, note=skill.note
                ) for skill in skill_data
            ]
        else:
            raise ValueError(f"Invalid user type: {user_type}")
        conn.add_all(objs)
        try:
            await conn.commit()
        except Exception as e:
            logger.error(f"Error attaching skills to intern: {e}")
            await conn.rollback()
            return False
        return True

    async def add_new_skill(
        self, conn: AsyncSession, skill: SkillCreate
    ):
        obj = Skill(**skill.model_dump())
        conn.add(obj)
        await conn.commit()
        await conn.refresh(obj)
        return obj

    async def add_new_skills(self, conn: AsyncSession, skills: list[SkillCreate]):
        objs = [Skill(**skill.model_dump()) for skill in skills]
        conn.add_all(objs)
        try:
            await conn.commit()
        except Exception as e:
            logger.error(f"Error adding new skills: {e}")
            await conn.rollback()
            return False
        return True

    # TODO: maybe add a caching layer
    async def get_available_skills(self, conn: AsyncSession, search_term: str | None = None):
        stmt = select(Skill)
        if search_term:
            stmt = stmt.where(
                Skill.name.ilike(f"%{search_term}%")
            )
        result = await conn.execute(stmt)
        return result.scalars()
