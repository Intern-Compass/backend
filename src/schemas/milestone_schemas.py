from datetime import date

from pydantic import BaseModel

from src.models.app_models import Milestone


class MilestoneInModel(BaseModel):
    project_id: str
    title: str
    description: str
    due_date: date
    status: str

class MilestoneOutModel(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    due_date: date
    status: str 

    @classmethod         
    def from_model(cls, milestone: Milestone) -> "MilestoneOutModel":
        return MilestoneOutModel(
            id=str(milestone.id),
            project_id=str(milestone.project_id),
            title=milestone.title,
            description=milestone.description,
            due_date=milestone.due_date,
            status=milestone.status
        )
