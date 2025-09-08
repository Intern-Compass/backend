from typing import Annotated
import uuid

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import ORJSONResponse

from src.schemas.skill_schemas import SkillCreate
from src.services.skill_service import SkillService

router: APIRouter = APIRouter(prefix="/intern", tags=["Intern"])

# TODO: refactor to be used by a logged in user
@router.post("/{user_id}/skills", tags=["Skills"])
async def add_skills_to_intern(
    user_id: uuid.UUID,
    skills: list[SkillCreate],
    skill_service: Annotated[SkillService, Depends()],
):
    """
    Attach skills to an intern.
    """
    await skill_service.add_skills_to_user(
        user_id=user_id, skills=skills
    )
    return ORJSONResponse({"message": "Skills added successfully"})
