from pydantic import BaseModel

from datetime import datetime
from uuid import UUID
from src.models.app_models import Project

class ProjectInModel(BaseModel):
    title: str
    description: str
    supervisor_id: str
    division_id: str

class ProjectOutModel(BaseModel):
    id: str
    title: str
    description: str
    supervisor_id: str
    division_id: str
    created_at: datetime    

    @classmethod         
    def from_model(project: Project) -> "ProjectOutModel":
        return ProjectOutModel(
            id=str(project.id),
            title=project.title,
            description=project.description,
            supervisor_id=project.supervisor_id,
            division_id=project.division_id,
            created_at=project.created_at
        )
