from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from src.schemas import UserInModel
from src.services.general_user_service import GeneralUserService

router: APIRouter = APIRouter(prefix="user/",tags=["GeneralUserRouter"])

@router.post
async def create_user(
        create_user_request: UserInModel,
        general_user_service: Annotated[GeneralUserService, Depends()]
):
    return await general_user_service.create_new_user(create_user_request)