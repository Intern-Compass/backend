from typing import Annotated, Any

from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.models import User
from src.repositories import UserRepository
from src.schemas import UserInModel, UserOutModel
from src.utils import hash_password


class GeneralUserService:
    def __init__(
            self,
            session: Annotated[AsyncSession, Depends(get_db_session)],
            repo: Annotated[UserRepository, Depends()]
    ):
        self.session = session
        self.user_repo = repo

    async def create_new_user(self, new_user: UserInModel) -> UserOutModel:
        # TODO: Confirm email before creating user
        # TODO: Send confirmation mail once user has been created
        # TODO: Send tokens as response to allow automatic login upon creation

        existing_user: User = await self.user_repo.get_user_by_email(conn=self.session, email=new_user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists. Please log in")

        new_user.password = hash_password(password=new_user.password)  # Hash password before persisting into DB
        created_user: User = await self.user_repo.create_new_user(conn=self.session, new_user=new_user)

        return UserOutModel.from_user(created_user)
