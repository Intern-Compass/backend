from typing import Annotated
import uuid

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import ORJSONResponse

from src.schemas import UserInModel, UserOutModel
from src.schemas.user_schemas import SkillAttachReq, SkillCreateReq, SkillRes, UserAccountTypeEmun
from src.services.general_user_service import GeneralUserService

router: APIRouter = APIRouter(tags=["GeneralUserRouter"])
"""Router concerns everything that is common to all users of the application. Add any common app endpoints here"""

@router.post("/user")
async def create_user(
        create_user_request: UserInModel,
        general_user_service: Annotated[GeneralUserService, Depends()]
) -> UserOutModel:
    return await general_user_service.create_new_user(create_user_request)


# TODO: refactor to be used by a logged in user
@router.post("/user/intern/{user_id}/skills")
async def add_skills_to_intern(
    user_id: uuid.UUID,
    skills: list[SkillAttachReq],
    general_user_service: Annotated[GeneralUserService, Depends()]
):
    """
    Attach skills to an intern.
    """
    await general_user_service.add_skills_to_user(
        user_id, UserAccountTypeEmun.intern.value, skills
    )
    # or jsend rs
    return ORJSONResponse({"message": "Skills added successfully"})


@router.get("/user/skills")
async def get_available_skills(
    general_user_service: Annotated[GeneralUserService, Depends()],
    search_query: str | None = None
) -> list[SkillRes]:
    val = await general_user_service.get_skills(search_query)
    return val

# TODO: refactor to be used by a logged in user
@router.post("/user/skill")
async def create_skill(
    skill: SkillCreateReq,
    created_by_user_id: uuid.UUID,
    general_user_service: Annotated[GeneralUserService, Depends()]
) -> SkillRes:
    return await general_user_service.create_new_skill(created_by_user_id, skill)
