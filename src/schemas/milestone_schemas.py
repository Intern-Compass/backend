from pydantic import BaseModel

from datetime import datetime, date
from uuid import UUID
from src.models.app_models import Milestone

class MilestoneInModel(BaseModel):
    title: str
    description: str
    due_date: date
    status: str

class MilestoneOutModel(BaseModel):
    id: str
    title: str
    description: str
    due_date: date
    status: str 

    @classmethod         
    def from_model(milestone: Milestone) -> "MilestoneOutModel":
        return MilestoneOutModel(
            id=milestone.id,
            title=milestone.title,
            description=milestone.description,
            due_date=milestone.due_date,
            status=milestone.status
        )
