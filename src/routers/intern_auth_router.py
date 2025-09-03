"""
This module would handle any thing regarding auth for an intern.
This includes:
    - Login
    - Logout
    - Registration
    - Forgot Password (Request)
    - Reset Password

    Will interface with the intern_service module to handle intern related stuff.
"""
from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.repositories import UserRepository
from src.models import User
from src.services import AuthService

router = APIRouter(prefix="/auth", tags=["AuthRouter"])



@router.post("/token")
async def login(
        form: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth_service: Annotated[AuthService, Depends()],
        request: Request
):
    """ Logs the user in and returns access and refresh tokens"""
    return await auth_service.login(
        username=form.username,
        password=form.password,
        req=request
    )
