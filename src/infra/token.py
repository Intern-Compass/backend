from abc import ABC
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from jwt import PyJWTError, decode, encode
from sqlalchemy import exists
from sqlalchemy.ext.asyncio import AsyncSession

from ..common import UserType
from ..models.app_models import Token
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
    async def new(
        cls,
        sub: str | UUID,
        data: dict | None = None,
        jti: str | None = None,
        now: datetime | None = None,
        expires_at: datetime | None = None,
    ) -> str:
        if isinstance(sub, UUID):
            sub = str(sub)
        now = now or datetime.now(UTC)
        expires_at = expires_at or datetime.now(UTC) + cls.token_type.lifetime
        return encode(
            payload={
                "data": data,
                "exp": expires_at,
                "iat": now,
                "jti": jti or str(uuid4()),
                "sub": sub,
                "type": cls.token_type,
            },
            key=settings.SECRET_KEY,
            algorithm=settings.ALGO,
        )

    @classmethod
    async def decode(cls, token: str) -> DecodedType:
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

        # # Attempting to convert sub to UUID
        # try:
        #     claims["sub"] = UUID(claims["sub"])
        # except ValueError:
        #     pass
        return claims


# noinspection PyMethodOverriding
class RevocableToken[DecodedType](BaseToken[DecodedType]):
    @classmethod
    async def _create_token_in_db(
        cls, conn: AsyncSession, expires_at: datetime
    ) -> Token:
        new_token = Token(expires_at=expires_at)
        conn.add(new_token)
        await conn.flush()
        await conn.refresh(new_token)
        return new_token

    @classmethod
    async def new(
        cls,
        conn: AsyncSession,
        sub: str | UUID,
        data: dict | None = None,
        jti: str | None = None,
    ) -> str:
        now = datetime.now(UTC)
        expires_at = now + cls.token_type.lifetime
        token_in_db = await cls._create_token_in_db(conn=conn, expires_at=expires_at)
        return await super().new(
            sub=sub, data=data, jti=str(token_in_db.jti), now=now, expires_at=expires_at
        )

    @classmethod
    async def _ensure_token_in_db(cls, conn: AsyncSession, jti: str) -> None:
        token_exists = await conn.scalar(
            exists(Token.__table__).where(Token.jti == jti).select()
        )
        if not token_exists:
            raise InvalidTokenError

    @classmethod
    async def decode(cls, conn: AsyncSession, token: str) -> dict:
        claims = await super().decode(token=token)
        # Ensuring the token is in the database
        if claims.get("jti"):
            jti = claims["jti"]
            await cls._ensure_token_in_db(conn=conn, jti=jti)
        else:
            raise InvalidTokenError
        return claims


class AccessToken(BaseToken[UserOutModel]):
    token_type = TokenType.ACCESS

    # noinspection PyMethodOverriding
    @classmethod
    async def new(cls, user: UserOutModel) -> str:
        user_id = user.user_id
        return await super().new(sub=user_id, data=user.model_dump())

    @classmethod
    async def decode(cls, token: str) -> UserOutModel:
        claims = await super().decode(token=token)
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


class PasswordResetToken[str](RevocableToken):
    token_type = TokenType.PASSWORD_RESET

    # noinspection PyMethodOverriding
    @classmethod
    async def new(cls, conn: AsyncSession, user_id: UUID) -> str:
        return await super().new(conn=conn, sub=user_id)

    @classmethod
    async def decode(cls, conn: AsyncSession, token: str) -> str:
        claims = await super().decode(conn=conn, token=token)
        user_id = claims["sub"]
        return user_id
