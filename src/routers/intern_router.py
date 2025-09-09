from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import ORJSONResponse

from src.schemas.skill_schemas import SkillCreate
from src.services.skill_service import SkillService
from src.utils import get_intern_user

router: APIRouter = APIRouter(prefix="/intern", tags=["Intern"])


# TODO: refactor to be used by a logged in user
@router.post("/skills", tags=["Skills"])
async def add_skills_to_intern(
    skills: list[SkillCreate],
    user: Annotated[dict, Depends(get_intern_user)],
    skill_service: Annotated[SkillService, Depends()],
):
    """
    Attach skills to an intern.
    """
    await skill_service.add_skills_to_user(user_id=user.get("sub"), skills=skills)
    return ORJSONResponse({"message": "Skills added successfully"})
