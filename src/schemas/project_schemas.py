from pydantic import BaseModel

from datetime import datetime
from uuid import UUID
from src.models.app_models import Project

class ProjectInModel(BaseModel):
    title: str
    description: str

class ProjectOutModel(BaseModel):
    id: str
    title: str
    description: str
    created_at: datetime    

    @classmethod         
    def from_model(project: Project) -> "ProjectOutModel":
        return ProjectOutModel(
            id=str(project.id),
            title=project.title,
            description=project.description,
            created_at=project.created_at
        )
