from typing import Annotated
import uuid

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import ORJSONResponse

from src.schemas.user_schemas import SkillAttachReq, UserAccountTypeEmun
from src.services.skill_service import SkillService

router: APIRouter = APIRouter(prefix="user", tags=["User"])
"""Router concerns everything that is common to all users of the application. Add any common app endpoints here"""

# TODO: refactor to be used by a logged in user
@router.post("/intern/{user_id}/skills", tags=["Intern", "Skills"])
async def add_skills_to_intern(
    user_id: uuid.UUID,
    skills: list[SkillAttachReq],
    skill_service: Annotated[SkillService, Depends(SkillService)],
):
    """
    Attach skills to an intern.
    """
    await skill_service.add_skills_to_user(
        user_id, UserAccountTypeEmun.intern.value, skills
    )
    return ORJSONResponse({"message": "Skills added successfully"})
