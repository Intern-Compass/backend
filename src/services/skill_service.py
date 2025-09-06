from typing import Annotated
import uuid

from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.repositories import SkillRepository
from src.schemas.user_schemas import SkillAttachReq, SkillCreate, SkillCreateReq, SkilledUserLitral, UserAccountTypeEmun

INTERN_USER_TYPE = UserAccountTypeEmun.intern.value
SUPERVISOR_USER_TYPE = UserAccountTypeEmun.supervisor.value

class SkillService:
    def __init__(
            self,
            session: Annotated[AsyncSession, Depends(get_db_session)],
            repo: Annotated[SkillRepository, Depends(SkillRepository)]
    ):
        self.session = session
        self.skill_repo = repo

    async def add_skills_to_user(
        self,
        user_id: uuid.UUID,
        user_type: SkilledUserLitral,
        skills: list[SkillAttachReq]
    ):
        async with self.session.begin():
            success = await self.skill_repo.attach_skills_to_user(self.session, user_id, user_type, skills)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add skills")

    async def get_skills(self, search_term: str | None = None):
        return await self.skill_repo.get_available_skills(self.session, search_term=search_term)

    async def create_new_skill(
        self,
        skill_creator_user_id: uuid.UUID,
        skill: SkillCreateReq
    ):
        skill = SkillCreate(
            created_by_user_id=skill_creator_user_id,
            **skill.model_dump()
        )
        try:
            async with self.session.begin():
                skill = await self.skill_repo.add_new_skill(self.session, skill)
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Skill already exists")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to create skill")
        return skill
