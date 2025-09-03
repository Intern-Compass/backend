from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from src.models import User

class UserInModel(BaseModel):
    email: str
    password: str

class UserOutModel(BaseModel):
    id: str
    email: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_user(cls, user: User) -> "UserOutModel":
        return UserOutModel(
            id=str(user.id),
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
