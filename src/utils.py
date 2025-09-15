import random
from enum import StrEnum
from typing import Annotated

import argon2
from argon2 import PasswordHasher
from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

from .logger import logger
from .schemas.user_schemas import UserOutModel, UserType
from .infra.token import InvalidTokenError, AccessToken
from .settings import settings

ph: PasswordHasher = PasswordHasher()


class TokenType(StrEnum):
    ACCESS = "access"
    PASSWORD_RESET = "password_reset"


def password_is_correct(user_password: str, supplied_password: str) -> bool:
    try:
        if ph.verify(user_password, supplied_password):
            return True
    except argon2.exceptions.VerifyMismatchError as e:
        logger.error(f"Invalid Password: {e}")
    return False


def hash_password(password: str) -> str:
    return ph.hash(password)


def generate_random_code() -> str:
    return str(random.randint(100000, 999999))


oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(
    token: Annotated[str, Depends(oauth_scheme)],
) -> UserOutModel:
    """
    Gets its token parameter from a FastAPI Dependency that checks the request for an "Authorization" header
    with a Bearer token.
    :param token: Bearer token
    :return: UserOutModel
    """
    try:
        payload: UserOutModel = AccessToken.decode(token=token)
        return payload
    except InvalidTokenError as e:
        logger.error(e)
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Session expired, log in again"
        )


def get_intern_user(payload: Annotated[UserOutModel, Depends(get_current_user)]):
    if payload.type == UserType.INTERN:
        return payload

    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Not in intern. You cannot access this endpoint.",
    )


def get_supervisor_user(payload: Annotated[UserOutModel, Depends(get_current_user)]):
    if payload.type == UserType.SUPERVISOR:
        return payload
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Not in supervisor. You cannot access this endpoint.",
    )


def normalize_string(string: str) -> str:
    return string.lower().strip()


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/hour"],
    enabled=settings.ENVIRONMENT == "production"
)
