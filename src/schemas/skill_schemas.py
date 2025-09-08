from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from src.schemas.user_schemas import UserAccountTypeEmun



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
