from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import Response

from src.schemas import UserInModel
from src.schemas.intern_schemas import InternInModel
from src.services import AuthService

router: APIRouter = APIRouter(prefix="/auth", tags=["Auth Router"])
"""Router concerns everything that has to do with authentication."""


@router.post("/supervisor")
async def create_supervisor(
    create_user_request: UserInModel,
    general_user_service: Annotated[AuthService, Depends()],
) -> dict[str, str]:
    return await general_user_service.create_unverified_new_user(create_user_request)


@router.post("/register")
async def create_intern(
    create_intern_request: InternInModel,
    general_user_service: Annotated[AuthService, Depends()],
) -> dict[str, str]:
    return await general_user_service.create_unverified_new_user(create_intern_request)


@router.post("/verify-code")
async def verify_user(
    verification_code: str, general_user_service: Annotated[AuthService, Depends()]
):
    return await general_user_service.verify_user(code=verification_code)


@router.post("/token")
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends()],
    response: Response,
):
    """Logs the intern in and returns access and refresh tokens"""
    return await auth_service.login(
        username=form.username, password=form.password, res=response
    )
