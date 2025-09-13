from abc import ABC
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from jwt import PyJWTError, decode, encode

from ..schemas import UserOutModel
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


class TokenBase(ABC):
    token_type: TokenType

    def new(self, sub: str | UUID, data: dict | None = None) -> str:
        if isinstance(sub, UUID):
            sub = str(sub)
        return encode(
            payload={
                "data": data,
                "exp": self.token_type.lifetime.total_seconds(),
                "iat": datetime.now(UTC),
                "jti": uuid4(),
                "sub": sub,
                "type": self.token_type,
            },
            key=settings.SECRET_KEY,
            algorithm=settings.ALGO,
        )

    @staticmethod
    def decode(token: str) -> dict:
        try:
            claims: dict = decode(
                token, key=settings.SECRET_KEY, algorithms=[settings.ALGO]
            )
        except PyJWTError:
            raise InvalidTokenError
        try:
            claims["sub"] = UUID(claims["sub"])
        except ValueError:
            pass
        return claims


class AccessToken(TokenBase):
    token_type = TokenType.ACCESS

    # noinspection PyMethodOverriding
    def new(self, user: UserOutModel) -> str:
        user_id = user.user_id
        return super().new(sub=user_id, data=user.model_dump())

    @staticmethod
    def decode(token: str) -> UserOutModel:
        claims = super().decode(token)
        data = claims["data"]
        return UserOutModel.model_validate(data)


class PasswordResetToken(TokenBase):
    token_type = TokenType.PASSWORD_RESET

    # noinspection PyMethodOverriding
    def new(self, user_id: UUID):
        return super().new(sub=user_id)

    @staticmethod
    def decode(token: str) -> UUID:
        claims = super().decode(token)
        user_id = claims["sub"]
        return user_id
