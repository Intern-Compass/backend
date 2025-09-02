from typing import Annotated, Any

from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.models import User
from src.repositories import UserRepository
from src.schemas import UserInModel


class GeneralUserService:
    def __init__(
            self,
            session: Annotated[AsyncSession, Depends(get_db_session)],
            repo: Annotated[UserRepository, Depends()]
    ):

        self.session = session
        self.user_repo = repo

    async def create_new_user(self, new_user: UserInModel):
        new_user_dict: dict[str, Any] = new_user.model_dump()

        existing_user: User = await self.user_repo.get_user_by_email(conn=self.session, email=new_user_dict.get("email"))
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists. Please log in")

        created_user: User = await self.user_repo.create(conn=self.session, values=new_user_dict)