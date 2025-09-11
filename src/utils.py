import random
from datetime import datetime, timedelta
from typing import Annotated

import argon2
from argon2 import PasswordHasher
from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from jose import jwt as jose_jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

from src.logger import logger
from src.schemas.user_schemas import UserOutModel, UserType
from src.settings import settings

ph: PasswordHasher = PasswordHasher()


def generate_access_token(user_to_login: UserOutModel) -> str:
    payload: dict = {
        "sub": user_to_login.user_id,
        **user_to_login.model_dump(exclude={"user_id"}),
        "exp": (datetime.now() + timedelta(minutes=60)),
    }

    access_token: str = jose_jwt.encode(
        claims=payload, key=settings.SECRET_KEY, algorithm=settings.ALGO
    )
    return access_token


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


def decode_token(token: str) -> dict:
    payload: dict = jwt.decode(
        token, key=settings.SECRET_KEY, algorithms=[settings.ALGO]
    )

    return payload


oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(
    token: Annotated[str, Depends(oauth_scheme)],
) -> dict:
    """
    Gets its token parameter from a FastAPI Dependency that checks the request for an "Authorization" header
    :param token:
    :return: user_data: str
    """
    try:
        payload: dict = decode_token(token)
        return payload
    except ExpiredSignatureError as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Session expired, log in again"
        )
    except DecodeError as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Session expired, log in again."
        )


def get_intern_user(payload: Annotated[dict, Depends(get_current_user)]):
    if payload.get("type") == UserType.INTERN:
        return payload

    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Not in intern. You cannot access this endpoint.",
    )


def get_supervisor_user(payload: Annotated[dict, Depends(get_current_user)]):
    if payload.get("type") == UserType.SUPERVISOR:
        return payload
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Not in supervisor. You cannot access this endpoint.",
    )


def normalize_email(email: str) -> str:
    return email.lower().strip()
