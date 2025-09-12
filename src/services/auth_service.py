from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import HTTPException, BackgroundTasks
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import (
    HTTP_409_CONFLICT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)

from src.repositories.general_user_repo import UserRepository
from src.models.app_models import User, VerificationCode
from src.db import get_db_session
from src.repositories.intern_repository import InternRepository
from src.repositories.verification_code_repo import VerificationCodeRepository
from src.schemas import UserInModel, InternInModel
from src.schemas.user_schemas import UserOutModel
from src.utils import (
    generate_access_token,
    password_is_correct,
    hash_password,
    generate_random_code,
    normalize_email,
    generate_password_reset_token,
)
from ..infra.email.contexts import (
    ResetPasswordEmailContext,
    VerifyEmailContext,
    EmailVerifiedContext,
    UpdatedUserContext,
)
from ..infra.email import send_email
from ..logger import logger


class AuthService:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        user_repo: Annotated[UserRepository, Depends()],
        intern_repo: Annotated[InternRepository, Depends()],
        code_repo: Annotated[VerificationCodeRepository, Depends()],
        background_task: BackgroundTasks,
    ):
        self.session = session
        self.user_repo = user_repo
        self.intern_repo = intern_repo
        self.code_repo = code_repo
        self.background_task = background_task

    # TODO: Rate limit
    async def create_unverified_new_user(
        self, new_user: UserInModel | InternInModel
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
                        detail="User already exists. Please log in",
                    )

                code: str = generate_random_code()
                await self.code_repo.upsert_code_with_user_id(
                    conn=self.session, user_id=existing_user.id, value=code
                )
                send_code = code
                user_email = normalize_email(existing_user.email)

            else:
                # TODO: refactor and simplify different user creation. To use Polymophic/Joined table inheritance

                # Hash password  when creating a new user
                new_user.password = hash_password(password=new_user.password)

                unverified_user: User = (
                    await self.intern_repo.create_new_intern(
                        conn=self.session, new_intern=new_user
                    )  # if the type is Intern
                    if isinstance(new_user, InternInModel)
                    else await self.user_repo.create_new_user(  # if type: any other type
                        conn=self.session, new_user=new_user
                    )
                    # TODO expand this to accomodate HR (admin) entities
                )

                code = generate_random_code()
                await self.code_repo.create_code(
                    conn=self.session, user_id=unverified_user.id, code=code
                )
                send_code = code
                user_email = normalize_email(unverified_user.email)

        # At this point, transaction has committed successfully
        print(f"Code for {user_email}: {send_code}")

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
            await self.code_repo.delete_code(conn=self.session, value=code)

            access_token: str = generate_access_token(
                UserOutModel.from_user(verified_user),
            )

        # Send confirmation mail once user has been created.
        user_normalized_email: str = normalize_email(verified_user.email)
        self.background_task.add_task(
            send_email,
            user_normalized_email,
            context=EmailVerifiedContext(),
        )
        return {"access_token": access_token, "token_type": "Bearer"}

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

        user_to_login: UserOutModel = UserOutModel.from_user(existing_user)

        access_token: str = generate_access_token(user_to_login)
        # new_refresh_token: str = await generate_refresh_token(
        #     existing_user.email, self.token_repo
        # )
        # set_custom_cookie(
        #     response=response,
        #     key="refresh_token",
        #     value=new_refresh_token,
        #     path="/auth",
        #     max_age=60 * 60 * 24 * 7,
        # )

        return {
            "access_token": access_token,
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

    # TODO: Rate limit
    async def request_reset_password(self, email: str):
        async with self.session.begin():
            user: User = await self.user_repo.get_user_by_email_or_phone(
                conn=self.session, email=email
            )
        if not user:
            logger.info(f"No user with email {email} exists to send verification code.")

        if user:
            token = generate_password_reset_token(user.email)
            user_email = user.email
            self.background_task.add_task(
                send_email,
                user_email,
                context=ResetPasswordEmailContext(token=token),
            )
        response = {
            "detail": "If this email exists, a password reset email will be sent."
        }
        return response

    async def verify_code_and_reset_password(self, code: str, new_password: str):
        async with self.session.begin():
            verified_code: bool | VerificationCode = await self._verify_code(
                code=code, conn=self.session
            )

            if not verified_code:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST, detail="Invalid verification code"
                )

            new_password: str = hash_password(new_password)
            values_to_update: dict = {"password": new_password}
            updated_user: User = await self.user_repo.update(
                conn=self.session,
                user_id=verified_code.user_id,
                values=values_to_update,
            )

        self.background_task.add_task(
            send_email,
            updated_user.email,
            context=UpdatedUserContext(values_updated=values_to_update),
        )
        return {
            "detail": "Your password has been reset successfully, please proceed to log in"
        }
