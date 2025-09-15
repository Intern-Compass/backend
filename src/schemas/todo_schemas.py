from datetime import datetime, date

from pydantic import UUID4, BaseModel

from src.models.app_models import Task, Todo


class TodoInModel(BaseModel):
    title: str
    description: str


class TodoUpdateModel(BaseModel):
    done: bool | None


class TodoOutModel(BaseModel):
    id: UUID4
    title: str
    details: str
    done: bool
    created_at: datetime
    updated_at: datetime
