from pydantic import BaseModel

from datetime import datetime
from uuid import UUID
from src.models.app_models import Note

class NoteInModel(BaseModel):
    content: str

class NoteOutModel(BaseModel):
    id: str
    content: str
    created_at: datetime    

    @classmethod         
    def from_model(note: Note) -> "NoteOutModel":
        return NoteOutModel(
            id=str(note.id),
            content=note.content,
            created_at=note.created_at
        )
