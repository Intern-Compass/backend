from typing import Annotated, Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.params import Depends
from fastapi import HTTPException

from src.db import get_db_session
from src.models.app_models import Todo
from src.repositories.intern_repo import InternRepository
from src.repositories.todo_repo import TodoRepository
from src.schemas.todo_schemas import TodoInModel, TodoUpdateModel, TodoOutModel


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

    async def get_todos(self, user_id: UUID, is_done: bool | None) -> list[TodoOutModel]:
        async with self.session.begin():
            intern = await self.intern_repo.get_intern_by_user_id(conn=self.session, user_id=user_id)
            if not intern:
                raise HTTPException(status_code=404, detail="Intern not found")

            todos: Sequence[Todo] = await self.todo_repo.get_todos_by_intern_id(
                conn=self.session,
                intern_id=intern.id,
                done=is_done,
            )

            return [
                TodoOutModel(
                    id=todo.id,
                    title=todo.title,
                    details=todo.details,
                    done=todo.done,
                    created_at=todo.created_at,
                    updated_at=todo.updated_at,
                )
                for todo in todos
            ]

    async def create_todo(self, user_id: UUID, todo_data: TodoInModel) -> TodoOutModel:
        async with self.session.begin():
            intern = await self.intern_repo.get_intern_by_user_id(self.session, user_id)
            if not intern:
                raise HTTPException(status_code=404, detail="Intern not found")
            todo: Todo = await self.todo_repo.create_todo(conn=self.session, intern_id=intern.id, todo_data=todo_data)

        return TodoOutModel(
            id=todo.id,
            title=todo.title,
            details=todo.details,
            done=todo.done,
            created_at=todo.created_at,
            updated_at=todo.updated_at
        )

    async def complete_todo(self, todo_id: UUID, intern_id: UUID) -> dict:
        async with self.session.begin():
            existing_todo: Todo = await self.todo_repo.get_todo_by_id(conn=self.session, todo_id=todo_id)
            if not existing_todo:
                raise HTTPException(status_code=404, detail="Todo not found")
            if existing_todo.intern_id != intern_id:
                raise HTTPException(status_code=403, detail="This is not your Todo to update.")

            todo_data = TodoUpdateModel(
                done=True
            )
            await self.todo_repo.update_todo(self.session, todo_id, todo_data)

        return {"detail": "Todo has been marked as completed"}