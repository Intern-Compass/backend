from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.app_models import InternSkill, Skill, SupervisorSkill
from src.schemas.user_schemas import UserAccountTypeEmun
from src.schemas.skill_schemas import SkillAttachReq, SkillCreate, SkilledUserLitral
from src.logger import logger




class SkillRepository:
    def __init__(self):
        self.table = Skill

    async def attach_skills_to_user(
        self, conn: AsyncSession, user_id: UUID,
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
            await conn.flush()
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
        await conn.flush()
        await conn.refresh(obj)
        return obj

    async def add_new_skills(self, conn: AsyncSession, skills: list[SkillCreate]):
        objs = [Skill(**skill.model_dump()) for skill in skills]
        conn.add_all(objs)
        try:
            await conn.flush()
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
