from datetime import datetime
from enum import Enum, unique
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict
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


@unique
class UserAccountTypeEmun(str, Enum):
    intern = "intern"
    supervisor = "supervisor"
    admin = "admin"


SkilledUserLitral = Literal[UserAccountTypeEmun.supervisor.value, UserAccountTypeEmun.intern.value]

# skill attach
class SkillAttachReq(BaseModel):
    id: UUID
    note: str | None = None


class SkillCreateReq(BaseModel):
    name: str
    description: str


class SkillCreate(SkillCreateReq):
    created_by_user_id: UUID


class SkillRes(BaseModel):
    id: UUID
    name: str
    description: str


class SkillDetaildRes(SkillRes):
    created_by_user_id: UUID
