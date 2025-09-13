from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.app_models import Intern, Todo
from src.schemas.todo import TodoInModel, TodoUpdateModel


class TodoRepository:
    def __init__(self):
        self.table = Todo

    async def get_todos_by_intern_id(
        self,
        conn: AsyncSession,
        intern_id: UUID,
        limit: int | None = None,
        offset: int | None = None,
        done: bool | None = None
    ) -> list[Todo]:
        stmt = (
            select(self.table)
            .join(Intern, Intern.id == self.table.intern_id)
            .where(Intern.id == intern_id)
        )

        if done is not None:
            stmt = stmt.where(self.table.done == done)

        if limit is not None:
            stmt = stmt.limit(limit)

        if offset is not None:
            stmt = stmt.offset(offset)

        result = await conn.execute(stmt)
        return result.scalars().all()

    async def create_todo(self, conn: AsyncSession, intern_id: UUID, todo_data: TodoInModel) -> Todo:
        obj = Todo(
            intern_id=intern_id,
            title=todo_data.title,
            details=todo_data.details,
        )
        conn.add(obj)
        await conn.flush()
        await  conn.refresh(obj)
        return obj

    async def update_todo(self, conn: AsyncSession, todo_id: UUID, todo_data: TodoUpdateModel) -> Todo | None:
        stmt = (
            update(self.table)
            .where(self.table.id == todo_id)
            .values(
                **{k: v for k, v in todo_data.dict(exclude_unset=True).items()}
            )
            .returning(self.table)
        )
        result = await conn.execute(stmt)
        await conn.flush()
        return result.scalar_one_or_none()
