from uuid import UUID

from sqlalchemy import select, Select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import User
from ..models.app_models import Skill
from ..schemas.skill_schemas import SkillCreate


class SkillRepository:
    def __init__(self):
        self.table = Skill

    async def create_or_get_skill(self, conn: AsyncSession, skill_name: str):
        stmt: Select = select(Skill).filter(Skill.name == skill_name)
        result: Result[Skill] = await conn.execute(stmt)
        existing_skill: Skill = result.scalars().first()

        if existing_skill:
            return existing_skill

        new_skill: Skill = self.table(name=skill_name)

        conn.add(new_skill)
        await conn.flush()
        await conn.refresh(new_skill)

        return new_skill

    async def attach_skills_to_user(
        self, conn: AsyncSession, user_id: UUID, skills: list[SkillCreate]
    ):
        skill_list = [
            (await self.create_or_get_skill(conn=conn, skill_name=skill.name))
            for skill in skills
        ]

        existing_user: User = (
            await conn.execute(
                select(User)
                .where(User.id == user_id)
                .options(selectinload(User.skills))
            )
        ).scalar_one_or_none()
        existing_user.skills.extend(skill_list)

        conn.add(existing_user)
        await conn.flush()

        return existing_user.skills

    async def add_new_skill(self, conn: AsyncSession, skill: SkillCreate):
        skill = self.table(name=skill.name)
        conn.add(skill)
        await conn.flush()
        await conn.refresh(skill)
        return skill

    async def add_new_skills(self, conn: AsyncSession, skills: list[SkillCreate]):
        skill_list = [self.table(name=skill.name) for skill in skills]
        conn.add_all(skill_list)
        await conn.flush()

        return skill_list

    # TODO: maybe add a caching layer
    async def get_available_skills(
        self, conn: AsyncSession, search_term: str | None = None
    ):
        stmt = select(self.table)
        if search_term:
            stmt = stmt.where(Skill.name.ilike(f"%{search_term}%"))
        result = await conn.execute(stmt)
        return result.scalars()
