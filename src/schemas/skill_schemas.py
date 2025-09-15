from pydantic import BaseModel


class SkillCreate(BaseModel):
    name: str


class SkillRes(BaseModel):
    name: str
