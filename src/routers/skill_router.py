from typing import Annotated
import uuid

from fastapi import APIRouter
from fastapi.params import Depends

from src.schemas.user_schemas import SkillCreateReq, SkillRes
from src.services.skill_service import SkillService

router: APIRouter = APIRouter(prefix="skills", tags=["Skills"])
"""Router concerns everything that is common to all users of the application. Add any common app endpoints here"""

@router.get("/skills")
async def get_available_skills(
    skill_service: Annotated[SkillService, Depends(SkillService)],
    search_query: str | None = None
) -> list[SkillRes]:
    val = await skill_service.get_skills(search_query)
    return val

# TODO: refactor to be used by a logged in user
@router.post("/skill")
async def create_skill(
    skill: SkillCreateReq,
    created_by_user_id: uuid.UUID,
    skill_service: Annotated[SkillService, Depends(SkillService)],
) -> SkillRes:
    return await skill_service.create_new_skill(created_by_user_id, skill)
