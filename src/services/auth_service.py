from datetime import datetime
from typing import Annotated
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import BackgroundTasks, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from ..common import UserType
from ..infra.token import (
    PasswordResetToken,
    AccessToken,
    RefreshToken,
    InvalidTokenError,
)
from ..db import get_db_session
from ..models.app_models import User, VerificationCode
from ..repositories.general_user_repo import UserRepository
from ..repositories.intern_repo import InternRepository
from ..repositories.verification_code_repo import VerificationCodeRepository
from ..schemas import InternInModel, UserInModel
from ..schemas.user_schemas import UserOutModel
from ..settings import settings
from ..utils import (
    generate_random_code,
    hash_password,
    normalize_string,
    password_is_correct,
)

from ..infra.email import send_email
from ..infra.email.contexts import (
    EmailVerifiedContext,
    ForgotPasswordContext,
    UpdatedUserContext,
    VerifyEmailContext,
)
from ..logger import logger
from ..repositories import SkillRepository
from ..repositories.supervisor_repo import SupervisorRepository
from ..schemas.intern_schemas import InternOutModel
from ..schemas.supervisor_schemas import SupervisorInModel, SupervisorOutModel


class AuthService:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        user_repo: Annotated[UserRepository, Depends()],
        intern_repo: Annotated[InternRepository, Depends()],
        supervisor_repo: Annotated[SupervisorRepository, Depends()],
        code_repo: Annotated[VerificationCodeRepository, Depends()],
        skill_repo: Annotated[SkillRepository, Depends()],
        background_task: BackgroundTasks,
    ):
        self.session = session
        self.user_repo = user_repo
        self.intern_repo = intern_repo
        self.supervisor_repo = supervisor_repo
        self.code_repo = code_repo
        self.skill_repo = skill_repo
        self.background_task = background_task

    @staticmethod
    async def _new_access_token_from_user(user: User) -> str:
        match user.type:
            case UserType.SUPERVISOR:
                user_to_login = SupervisorOutModel.from_supervisor(user)
            case UserType.INTERN:
                user_to_login = InternOutModel.from_intern(user)
            case _:
                user_to_login = UserOutModel.from_user(user)

        return await AccessToken.new(user=user_to_login)

    async def create_unverified_new_user(
        self, new_user: UserInModel | InternInModel | SupervisorInModel
    ) -> dict[str, str]:
        async with self.session.begin():  # Transactional, for atomicity
            existing_user: User = await self.user_repo.get_user_by_email_or_phone(
                conn=self.session,
                email=new_user.email,
                phone_number=new_user.phone_number,
            )

            if existing_user:
                if existing_user.verified:
                    raise HTTPException(
                        status_code=HTTP_409_CONFLICT,
                        detail="User already exists with specified email or phone number. Please log in",
                    )

                # The user exists but isn't verified yet
                code: str = generate_random_code()
                await self.code_repo.upsert_code_with_user_id(
                    conn=self.session, user_id=existing_user.id, value=code
                )
                send_code = code
                user_email = normalize_string(existing_user.email)

            else:
                # Hash password  when creating a new user
                new_user.password = hash_password(password=new_user.password)

                unverified_user: User = await self.user_repo.create_new_user(
                    conn=self.session, new_user=new_user, skill_repo=self.skill_repo
                )

                if isinstance(new_user, InternInModel):
                    unverified_user: User = await self.intern_repo.create_new_intern(
                        conn=self.session, new_intern=new_user, user=unverified_user
                    )
                elif isinstance(new_user, SupervisorInModel):
                    unverified_user: User = (
                        await self.supervisor_repo.create_new_supervisor(
                            conn=self.session,
                            new_supervisor=new_user,
                            user=unverified_user,
                        )
                    )

                code = generate_random_code()
                await self.code_repo.create_code(
                    conn=self.session, user_id=unverified_user.id, code=code
                )
                send_code = code
                user_email = normalize_string(unverified_user.email)

        # Send verification code to email
        self.background_task.add_task(
            send_email,
            user_email,
            context=VerifyEmailContext(send_code=send_code),
        )

        return {"detail": "Verification code sent to email"}

    async def verify_user(self, code: str) -> dict[str, str]:
        async with self.session.begin():  # Transactional, for atomicity
            verification_code: VerificationCode = await self.code_repo.get_code(
                conn=self.session, value=code
            )
            if not verification_code:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST, detail="Invalid verification code"
                )

            verified_user: User = await self.user_repo.update(
                conn=self.session,
                user_id=verification_code.user_id,
                values={"verified": True},
            )
            if not verified_user:
                raise HTTPException(
                    status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Something went wrong with verification",
                )

            await self.code_repo.delete_code(conn=self.session, value=code)

            match verified_user.type:
                case UserType.SUPERVISOR:
                    logger.info(
                        f"Supervisor user {verified_user.email} has been verified"
                    )
                case UserType.INTERN:
                    logger.info(f"Intern user {verified_user.email} has been verified")
                case _:
                    logger.info(f"User {verified_user.email} has been verified")

            access_token: str = await self._new_access_token_from_user(verified_user)

        # Send confirmation mail once user has been created.
        user_normalized_email: str = normalize_string(verified_user.email)
        self.background_task.add_task(
            send_email,
            user_normalized_email,
            context=EmailVerifiedContext(),
        )
        return {
            "access_token": access_token,
            "user_type": verified_user.type,
            "token_type": "Bearer",
        }

    async def login(self, username: str, password: str):
        existing_user: User = await self.user_repo.get_user_by_email_or_phone(
            conn=self.session, email=username
        )
        if not existing_user:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Invalid login credentials"
            )

        if not password_is_correct(existing_user.password, password):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Invalid login credentials"
            )

        if not existing_user.verified:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Invalid login credentials"
            )

        access_token: str = await self._new_access_token_from_user(existing_user)

        return {
            "access_token": access_token,
            "user_type": existing_user.type,
            "token_type": "Bearer",
        }

    async def _verify_code(
        self, code: str, conn: AsyncSession
    ) -> bool | VerificationCode:
        """Central method for verifying a code."""
        verification_code: VerificationCode = await self.code_repo.get_code(
            conn=conn, value=code
        )

        if not verification_code:
            return False
        elif verification_code.expires_at <= datetime.now(tz=ZoneInfo("UTC")):
            return False
        else:
            await self.code_repo.delete_code(conn=conn, value=code)
            return verification_code

    async def request_reset_password(self, email: str):
        async with self.session.begin():
            user: User = await self.user_repo.get_user_by_email_or_phone(
                conn=self.session, email=email
            )
        if not user:
            logger.info(f"No user with email {email} exists to send verification code.")

        if user:
            token = PasswordResetToken.new(user_id=user.id)
            user_email = user.email
            self.background_task.add_task(
                send_email,
                user_email,
                context=ForgotPasswordContext(
                    reset_link=f"{settings.FRONTEND_URL}?reset_link={token}"
                ),
            )
        response = {
            "detail": "If this email exists, a password reset email will be sent."
        }
        return response

    async def reset_password(self, user_id: UUID, new_password: str):
        new_password: str = hash_password(new_password)
        values_to_update: dict = {"password": new_password}
        updated_user: User = await self.user_repo.update(
            conn=self.session,
            user_id=user_id,
            values=values_to_update,
        )

        self.background_task.add_task(
            send_email,
            updated_user.email,
            context=UpdatedUserContext(values_updated=list(values_to_update.keys())),
        )
        return {
            "detail": "Your password has been reset successfully, please proceed to log in"
        }

    async def refresh_token(self, token: str):
        try:
            user_id: str = await RefreshToken.decode(self.session, token)
        except InvalidTokenError:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        user = await self.user_repo.get_user_by_id(
            conn=self.session, user_id=UUID(user_id)
        )
        if not user:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        access_token: str = await self._new_access_token_from_user(user)

        return {
            "access_token": access_token,
            "user_type": user.type,
            "token_type": "Bearer",
        }
