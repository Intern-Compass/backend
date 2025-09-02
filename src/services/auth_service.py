from typing import Annotated

from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.logger import logger
from src.repositories.user_repo import UserRepository
from src.models.app_models import User
from src.db import get_db_session
from src.schemas.user_schemas import UserOutModel
from src.utils import generate_access_token, password_is_correct


class AuthService:
    def __init__(
            self,
            user_repo: Annotated[UserRepository, Depends()],
            session: Annotated[AsyncSession, Depends(get_db_session)]
    ):
        self.user_repo = user_repo
        self.session = session

    async def login(self, username: str, password: str, req: Request):
        existing_user: User = await self.user_repo.get_user_by_email(conn=self.session, email=username)
        if not existing_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")


        if not password_is_correct(existing_user.password_hash, password):
            raise HTTPException(status_code=401, detail="Invalid login credentials")

        user_to_login: UserOutModel = UserOutModel.from_user(existing_user)
        try:
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

        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            raise HTTPException(
                status_code=500, detail="an error occurred while logging in the user"
            )