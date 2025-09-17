from datetime import datetime
from pydantic import BaseModel

from ..models.app_models import Project


class ProjectInModel(BaseModel):
    title: str
    description: str


class ProjectOutModel(BaseModel):
    id: str
    title: str
    description: str
    supervisor_id: str
    department_id: str
    created_at: datetime

    @classmethod
    def from_model(cls, project: Project) -> "ProjectOutModel":
        return ProjectOutModel(
            id=str(project.id),
            title=project.title,
            description=project.description,
            supervisor_id=str(project.supervisor_id),
            department_id=str(project.department_id),
            created_at=project.created_at,
        )
