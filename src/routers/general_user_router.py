from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from src.schemas import UserInModel, UserOutModel
from src.services.general_user_service import GeneralUserService

router: APIRouter = APIRouter(tags=["GeneralUserRouter"])
"""Router concerns everything that is common to all users of the application. Add any common app endpoints here"""

@router.post("/user")
async def create_user(
        create_user_request: UserInModel,
        general_user_service: Annotated[GeneralUserService, Depends()]
) -> UserOutModel:
    return await general_user_service.create_new_user(create_user_request)