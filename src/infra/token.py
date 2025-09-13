from abc import ABC
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from jwt import PyJWTError, decode, encode

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

    def new(self, sub: str | UUID) -> str:
        if isinstance(sub, UUID):
            sub = str(sub)
        return encode(
            payload={
                "exp": self.token_type.lifetime.total_seconds(),
                "iat": datetime.now(UTC),
                "jti": uuid4(),
                "sub": sub,
                "type": self.token_type,
            },
            key=settings.SECRET_KEY,
            algorithm=settings.ALGO,
        )

    def decode(self, token: str) -> str | UUID:
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


class PasswordResetToken(TokenBase):
    token_type = TokenType.PASSWORD_RESET
