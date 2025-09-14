import uuid
from typing import Annotated
from uuid import UUID

from pydantic import UUID4

from fastapi import APIRouter
from fastapi.params import Depends

from ..schemas.intern_schemas import ISupervisor, InternOutModel, BasicUserDetails
from ..schemas.project_schemas import ProjectOutModel
from ..schemas.task_schemas import TaskOutModel
from ..schemas.todo_schemas import TodoInModel, TodoOutModel
from ..services.intern_service import InternService
from ..services.todo_service import TodoService
from ..utils import get_intern_user


router: APIRouter = APIRouter(prefix="/intern", tags=["Intern"])


@router.get("/supervisor", tags=["Dashboard"])
async def get_intern_supervisor(
    user: Annotated[InternOutModel, Depends(get_intern_user)],
    intern_service: Annotated[InternService, Depends()],
) -> BasicUserDetails:
    supervisor = await intern_service.get_supervisor_by_intern_id(
        intern_id=uuid.UUID(user.intern_id)
    )
    return supervisor


@router.get("/tasks", tags=["Tasks", "Dashboard"])
async def get_intern_tasks(
    user: Annotated[InternOutModel, Depends(get_intern_user)],
    intern_service: Annotated[InternService, Depends()],
) -> list[TaskOutModel]:
    return await intern_service.get_tasks(user_id=uuid.UUID(user.user_id))


@router.get("/projects", tags=["Projects", "Dashboard"])
async def get_projects(
    user: Annotated[InternOutModel, Depends(get_intern_user)],
    intern_service: Annotated[InternService, Depends()],
) -> list[ProjectOutModel]:
    return await intern_service.get_projects(intern_id=uuid.UUID(user.intern_id))


@router.get("/todos", tags=["Todos", "Dashboard"])
async def get_intern_todos(
    user: Annotated[InternOutModel, Depends(get_intern_user)],
    todo_service: Annotated[TodoService, Depends()],
    is_done: bool | None = None,
) -> list[TodoOutModel]:
    todos = await todo_service.get_todos(user_id=UUID(user.user_id), is_done=is_done)
    return todos


@router.post("/todos", tags=["Todos", "Dashboard"], status_code=201)
async def create_intern_todo(
    todo_data: TodoInModel,
    user: Annotated[InternOutModel, Depends(get_intern_user)],
    todo_service: Annotated[TodoService, Depends()],
) -> TodoOutModel:
    return await todo_service.create_todo(
        user_id=UUID(user.user_id), todo_data=todo_data
    )

@router.patch("/todos/{todo_id}/complete", tags=["Todos", "Dashboard"])
async def complete_intern_todo(
    todo_id: UUID4,
    todo_service: Annotated[TodoService, Depends()],
    intern: Annotated[InternOutModel, Depends(get_intern_user)],
):
    return await todo_service.complete_todo(
        todo_id=todo_id, intern_id=UUID(intern.intern_id)
    )
