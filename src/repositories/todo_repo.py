from typing import Sequence
from uuid import UUID

from sqlalchemy import select, update, Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.app_models import Intern, Todo
from src.schemas.todo_schemas import TodoInModel, TodoUpdateModel


class TodoRepository:
    def __init__(self):
        self.table = Todo

    async def get_todos_by_intern_id(
        self, conn: AsyncSession, intern_id: UUID, done: bool | None = None
    ) -> Sequence[Todo]:
        stmt = (
            select(self.table)
            .join(Intern, Intern.id == self.table.intern_id)
            .where(Intern.id == intern_id)
        )

        if done is not None:
            stmt = stmt.where(self.table.done == done)

        result = await conn.execute(stmt)
        return result.scalars().all()

    async def create_todo(
        self, conn: AsyncSession, intern_id: UUID, todo_data: TodoInModel
    ) -> Todo:
        todo = self.table(
            intern_id=intern_id,
            title=todo_data.title,
            details=todo_data.description,
        )
        conn.add(todo)
        await conn.flush()
        await conn.refresh(todo)
        return todo

    async def update_todo(
        self, conn: AsyncSession, todo_id: UUID, todo_data: TodoUpdateModel
    ) -> Todo | None:
        stmt = (
            update(self.table)
            .where(self.table.id == todo_id)
            .values(**dict(todo_data.model_dump(exclude_unset=True).items()))
            .returning(self.table)
        )
        result = await conn.execute(stmt)
        await conn.flush()
        return result.scalar_one_or_none()

    async def get_todo_by_id(self, conn: AsyncSession, todo_id: UUID):
        stmt = select(self.table).where(self.table.id == todo_id)
        result: Result = await conn.execute(stmt)
        return result.scalar_one_or_none()
