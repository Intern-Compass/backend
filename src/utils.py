import argon2
from argon2 import PasswordHasher
from jose import jwt

from src.logger import logger
from src.schemas.user_schemas import UserOutModel
from src.settings import settings

ph: PasswordHasher = PasswordHasher()


def generate_access_token(
    user_to_login: UserOutModel,
) -> str:
    payload: dict = user_to_login.model_dump()

    access_token: str = jwt.encode(
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