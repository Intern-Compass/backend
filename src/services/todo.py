from typing import Annotated
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.params import Depends
from fastapi import HTTPException

from src.db import get_db_session
from src.models.app_models import Todo
from src.repositories.intern_repository import InternRepository
from src.repositories.todo import TodoRepository
from src.schemas.todo import TodoInModel, TodoUpdateModel


class TodoService:

    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        intern: Annotated[InternRepository, Depends()],
        todo: Annotated[TodoRepository, Depends()]
    ) -> None:
        self.session = session
        self.todo_repo = todo
        self.intern_repo = intern

    async def get_todo(self, user_id: UUID, done: bool | None, limit: int | None, offset: int | None) -> list[Todo]:
        async with self.session.begin():
            intern = await self.intern_repo.get_intern_by_user_id(self.session, user_id)
            if not intern:
                raise HTTPException(status_code=404, detail="Intern not found")
            return await self.todo_repo.get_todos_by_intern_id(
                self.session,
                intern.id,
                limit,
                offset,
                done,
            )

    async def create_todo(self, user_id: UUID, todo_data: TodoInModel) -> Todo:
        async with self.session.begin():
            intern = await self.intern_repo.get_intern_by_user_id(self.session, user_id)
            if not intern:
                raise HTTPException(status_code=404, detail="Intern not found")
            return await self.todo_repo.create_todo(self.session, intern.id, todo_data)

    async def complete_todo(self, todo_id: UUID) -> None:
        async with self.session.begin():
            todo_data = TodoUpdateModel(
                done=True
            )
            if not (await self.todo_repo.update_todo(self.session, todo_id, todo_data)):
                raise HTTPException(status_code=404, detail="Todo not found")
