from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.models.app_models import Note


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
    def from_model(cls, note: Note) -> "NoteOutModel":
        return NoteOutModel(
            id=str(note.id),
            content=note.content,
            intern_id=str(note.intern_id),
            task_id=note.task_id,
            created_at=note.created_at,
        )
