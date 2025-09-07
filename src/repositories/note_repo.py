from sqlalchemy import Select, select, Result, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.app_models import Note
from src.schemas.note_schemas import NoteInModel
from typing import Optional, List

class NoteRepository:
    def __init__(self):
        self.table = Note

    async def create_new_note(self, new_note: NoteInModel, conn: AsyncSession):
        note: Note = Note(
            intern_id=new_note.intern_id,
            task_id=new_note.task_id,
            content=new_note.content
        )
        conn.add(note)        
        await conn.refresh(note)
        return note
    
    async def get_note_by_id(self, conn: AsyncSession, id_value: str):
        stmt = select(self.table).where(self.table.id == id_value)
        result = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_notes(self, conn: AsyncSession):
        stmt = select(self.table)
        result = await conn.execute(stmt)
        return result.scalars().all()
    
    async def get_notes_by_task_id(self, conn: AsyncSession, task_id):
        stmt = select(self.table).where(self.table.task_id == task_id)
        result = await conn.execute(stmt)
        return result.scalars().all()
    
    async def get_all_notes_by_intern_id(self, conn: AsyncSession, intern_id):
        stmt = select(self.table).where(self.table.intern_id == intern_id)
        result = await conn.execute(stmt)
        return result.scalars().all()
    
    async def update_note(self, conn: AsyncSession, id_value: str, values: dict):
        stmt = (
            update(self.table)
            .where(self.table.id == id_value)
            .values(**values)
            .returning(self.table)
        )
        result = await conn.execute(stmt)         
        return result.scalar_one_or_none()

    async def delete_note(self, conn: AsyncSession, id_value: str) -> None:
        stmt = delete(self.table).where(self.table.id == id_value)
        await conn.execute(stmt)        

