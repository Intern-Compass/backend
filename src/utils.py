import random

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
    payload: dict = {
        "sub": user_to_login.id,
        "firstname": user_to_login.firstname,
        "lastname": user_to_login.lastname,
        "phone_number": user_to_login.phone_number,
        "email": user_to_login.email,
        # "created_at": user_to_login.created_at # Not json serializable
    }

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

def hash_password(password: str) -> str:
    return ph.hash(password)

def generate_random_code() -> str:
    return str(random.randint(100000, 999999))