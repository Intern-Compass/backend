from datetime import datetime, date

from pydantic import BaseModel

from src.models.app_models import Task


class TaskInModel(BaseModel):
    project_id: str
    title: str
    description: str
    due_date: date


class TaskOutModel(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    due_date: date
    created_at: datetime

    @classmethod
    def from_model(cls, task: Task) -> "TaskOutModel":
        return TaskOutModel(
            id=str(task.id),
            project_id=str(task.project_id),
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            created_at=task.created_at,
        )
