from typing import Annotated
import uuid
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_409_CONFLICT

from src.db import get_db_session
from src.models import User
from src.models.app_models import Skill
from src.repositories import SkillRepository, UserRepository
from src.schemas.skill_schemas import SkillCreate, SkillRes


class SkillService:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        repo: Annotated[SkillRepository, Depends()],
        user_repo: Annotated[UserRepository, Depends()]
    ):
        self.session = session
        self.skill_repo = repo
        self.user_repo = user_repo

    async def add_skills_to_user(self, user_id: uuid.UUID, skills: list[SkillCreate]):
        async with self.session.begin():
            await self.skill_repo.attach_skills_to_user(
                conn=self.session, user_id=user_id, skills=skills
            )

        return {"message": "Skills added successfully"}

    async def get_skills(self, search_term: str | None = None):
        return await self.skill_repo.get_available_skills(
            conn=self.session, search_term=search_term
        )

    async def create_new_skill(self, skill: SkillCreate):
        try:
            async with self.session.begin():
                skill = await self.skill_repo.add_new_skill(
                    conn=self.session, skill=skill
                )
        except IntegrityError:
            raise HTTPException(
                status_code=HTTP_409_CONFLICT, detail="Skill already exists"
            )

        return skill

    async def get_user_skills(self, user_id: UUID) -> list[SkillRes]:
        async with self.session.begin():
            user: User = await self.user_repo.get_by_id(conn=self.session, user_id=user_id)

        return [SkillRes(name=skill.name) for skill in user.skills]
