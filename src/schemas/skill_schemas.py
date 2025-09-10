from uuid import UUID

from pydantic import BaseModel


class SkillCreate(BaseModel):
    name: str


class SkillRes(BaseModel):
    id: UUID
    name: str
