from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Depends

from src.schemas import UserOutModel
from src.schemas.skill_schemas import SkillRes, SkillCreate
from src.services.skill_service import SkillService
from src.utils import get_current_user

router: APIRouter = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("/", tags=["Onboarding Page"])
async def get_all_available_skills(
    skill_service: Annotated[SkillService, Depends()], search_query: str | None = None
) -> list[SkillRes]:
    skills = await skill_service.get_skills(search_query)
    return skills


@router.post("/", tags=["Profile", "Skills"])
async def add_skills_to_user(
    skills: list[SkillCreate],
    user: Annotated[UserOutModel, Depends(get_current_user)],
    skill_service: Annotated[SkillService, Depends()],
):
    """
    Attach skills to a user.
    """
    return await skill_service.add_skills_to_user(
        user_id=UUID(user.user_id), skills=skills
    )


@router.get("/get-user-skills", tags=["Profile", "Skills"])
async def get_user_skills(
    user: Annotated[UserOutModel, Depends(get_current_user)],
    skill_service: Annotated[SkillService, Depends()],
) -> list[SkillRes]:
    return await skill_service.get_user_skills(user_id=UUID(user.user_id))
