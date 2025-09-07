from pydantic import BaseModel

from datetime import datetime
from uuid import UUID
from src.models.app_models import Note
from typing import Optional

class NoteInModel(BaseModel):
    intern_id: str
    task_id: Optional[str]
    content: str

class NoteOutModel(BaseModel):
    id: str
    content: str
    intern_id: str
    task_id: Optional[str]
    created_at: datetime    

    @classmethod         
    def from_model(note: Note) -> "NoteOutModel":
        return NoteOutModel(
            id=str(note.id),
            content=note.content,
            intern_id=note.intern_id,
            task_id=note.task_id,
            created_at=note.created_at
        )
