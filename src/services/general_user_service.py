from typing import Annotated, Any, Literal
import uuid

from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.models import User
from src.repositories import UserRepository
from src.schemas import UserInModel, UserOutModel
from src.schemas.user_schemas import SkillAttachReq, SkillCreate, SkillCreateReq, SkilledUserLitral, UserAccountTypeEmun
from src.utils import hash_password

INTERN_USER_TYPE = UserAccountTypeEmun.intern.value
SUPERVISOR_USER_TYPE = UserAccountTypeEmun.supervisor.value

class GeneralUserService:
    def __init__(
            self,
            session: Annotated[AsyncSession, Depends(get_db_session)],
            repo: Annotated[UserRepository, Depends()]
    ):
        self.session = session
        self.user_repo = repo

    async def create_new_user(self, new_user: UserInModel) -> UserOutModel:
        # TODO: Confirm email before creating user
        # TODO: Send confirmation mail once user has been created
        # TODO: Send tokens as response to allow automatic login upon creation

        existing_user: User = await self.user_repo.get_user_by_email(conn=self.session, email=new_user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists. Please log in")

        new_user.password = hash_password(password=new_user.password)  # Hash password before persisting into DB
        created_user: User = await self.user_repo.create_new_user(conn=self.session, new_user=new_user)

        return UserOutModel.from_user(created_user)

    async def add_skills_to_user(
        self,
        user_id: uuid.UUID,
        user_type: SkilledUserLitral,
        skills: list[SkillAttachReq]
    ):
        success = await self.user_repo.attach_skills_to_user(self.session, user_id, user_type, skills)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add skills")

    async def get_skills(self, search_term: str | None = None):
        return await self.user_repo.get_available_skills(self.session, search_term=search_term)

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
            skill = await self.user_repo.add_new_skill(self.session, skill)
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Skill already exists")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to create skill")
        return skill
