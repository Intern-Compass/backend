from abc import ABC
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from jwt import PyJWTError, decode, encode

from ..common import UserType
from ..schemas import UserOutModel
from ..schemas.intern_schemas import InternOutModel
from ..schemas.supervisor_schemas import SupervisorOutModel
from ..settings import settings


class InvalidTokenError(Exception):
    pass


class TokenType(StrEnum):
    ACCESS = "access"
    PASSWORD_RESET = "password_reset"

    @property
    def lifetime(self) -> timedelta:
        return TOKEN_LIFETIMES[self]


TOKEN_LIFETIMES: dict[TokenType, timedelta] = {
    TokenType.ACCESS: timedelta(minutes=60),
    TokenType.PASSWORD_RESET: timedelta(minutes=10),
}


class BaseToken[DecodedType](ABC):
    token_type: TokenType

    @classmethod
    def new(cls, sub: str | UUID, data: dict | None = None) -> str:
        if isinstance(sub, UUID):
            sub = str(sub)
        now = datetime.now(UTC)
        return encode(
            payload={
                "data": data,
                "exp": now + cls.token_type.lifetime,
                "iat": now,
                "jti": uuid4().hex,
                "sub": sub,
                "type": cls.token_type,
            },
            key=settings.SECRET_KEY,
            algorithm=settings.ALGO,
        )

    @classmethod
    def decode(cls, token: str) -> DecodedType:
        # Actual decoding
        try:
            claims: dict = decode(
                token, key=settings.SECRET_KEY, algorithms=[settings.ALGO]
            )
        except PyJWTError:
            raise InvalidTokenError

        # Validating the token type
        if claims.get("type") != cls.token_type.value:
            raise InvalidTokenError

        # Attempting to convert sub to UUID
        try:
            claims["sub"] = UUID(claims["sub"])
        except ValueError:
            pass
        return claims


class AccessToken(BaseToken[UserOutModel]):
    token_type = TokenType.ACCESS

    # noinspection PyMethodOverriding
    @classmethod
    def new(cls, user: UserOutModel) -> str:
        user_id = user.user_id
        return super().new(sub=user_id, data=user.model_dump())

    @classmethod
    def decode(cls, token: str) -> UserOutModel:
        claims = super().decode(token)
        data = claims["data"]
        data["user_id"] = claims["sub"]
        data["type"] = UserType(data["type"])
        match data["type"]:
            case UserType.SUPERVISOR:
                return SupervisorOutModel.model_validate(data)
            case UserType.INTERN:
                return InternOutModel.model_validate(data)
            case _:
                return UserOutModel.model_validate(data)


class PasswordResetToken(BaseToken):
    token_type = TokenType.PASSWORD_RESET

    # noinspection PyMethodOverriding
    @classmethod
    def new(cls, user_id: UUID) -> str:
        return super().new(sub=user_id)

    @classmethod
    def decode(cls, token: str) -> UUID:
        claims = super().decode(token)
        user_id = claims["sub"]
        return user_id
