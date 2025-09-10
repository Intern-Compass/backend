from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from src.schemas.skill_schemas import SkillRes, SkillCreate
from src.services.skill_service import SkillService

router: APIRouter = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("/")
async def get_available_skills(
    skill_service: Annotated[SkillService, Depends()], search_query: str | None = None
) -> list[SkillRes]:
    skills = await skill_service.get_skills(search_query)
    return skills


# TODO: refactor to be used by a logged in user
@router.post("/")
async def create_skill(
    skill: SkillCreate,
    skill_service: Annotated[SkillService, Depends()],
) -> SkillRes:
    return await skill_service.create_new_skill(skill=skill)
