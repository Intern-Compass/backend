from datetime import datetime

from pydantic import BaseModel
from src.models import User

class UserInModel(BaseModel):
    email: str
    password: str

class UserOutModel(BaseModel):
    email: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_user(cls, user: User) -> "UserOutModel":
        return UserOutModel(
            email=user.c.email,
            created_at=user.c.created_at,
            updated_at=user.c.updated_at,
        )
