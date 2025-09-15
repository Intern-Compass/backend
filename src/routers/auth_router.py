from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import Response

from ..schemas.intern_schemas import InternInModel
from ..schemas.supervisor_schemas import SupervisorInModel
from ..schemas.user_schemas import ResetPasswordRequest, UserEmail, VerificationCode
from ..services import AuthService

from ..infra.token import PasswordResetToken

router: APIRouter = APIRouter(prefix="/auth", tags=["Auth Router"])
"""Router concerns everything that has to do with authentication."""


@router.post("/register-supervisor")
async def create_supervisor(
    create_supervisor_request: SupervisorInModel,
    general_user_service: Annotated[AuthService, Depends()],
) -> dict[str, str]:
    return await general_user_service.create_unverified_new_user(
        create_supervisor_request
    )


@router.post("/register-intern")
async def create_intern(
    create_intern_request: InternInModel,
    general_user_service: Annotated[AuthService, Depends()],
) -> dict[str, str]:
    return await general_user_service.create_unverified_new_user(create_intern_request)


@router.post("/verify-code")
async def verify_user_and_create(
    code: VerificationCode, general_user_service: Annotated[AuthService, Depends()]
):
    return await general_user_service.verify_user(code=code.code)


@router.post("/token")
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends()],
    response: Response,
):
    """Logs the intern in and returns access and refresh tokens"""
    return await auth_service.login(username=form.username, password=form.password)


@router.post("/forgot-password")
async def request_request_password(
    auth_service: Annotated[AuthService, Depends()],
    user_email: UserEmail,
) -> dict[str, str]:
    return await auth_service.request_reset_password(email=user_email.email)


@router.post("/reset-password")
async def reset_password(
    details: ResetPasswordRequest,
    auth_service: Annotated[AuthService, Depends()],
):
    user_id: str = PasswordResetToken.decode(details.token)
    return await auth_service.reset_password(
        user_id=UUID(user_id), new_password=details.password
    )
