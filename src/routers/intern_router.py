from typing import Annotated

from pydantic import UUID4

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import ORJSONResponse

from ..schemas import UserOutModel
from ..schemas.intern_schemas import ISupervisor
from ..schemas.project_schemas import ProjectOutModel
from ..schemas.task_schemas import TaskOutModel
from ..schemas.todo import TodoInModel, TodoOutModel
from ..services.intern_service import InternService
from ..services.todo import TodoService
from ..utils import get_intern_user


router: APIRouter = APIRouter(prefix="/intern", tags=["Intern"])


@router.get("/supervisor", tags=["Dashboard"])
async def get_intern_supervisor(
    user: Annotated[UserOutModel, Depends(get_intern_user)],
    intern_service: Annotated[InternService, Depends()],
) -> ISupervisor:
    supervisor = await intern_service.get_supervisor_by_intern_user_id(user.user_id)
    if supervisor:
        return supervisor
    return ORJSONResponse({"message": "Supervisor not found"}, status_code=404)


@router.get("/task", tags=["Tasks", "Dashboard"])
async def get_intern_tasks(
    user: Annotated[UserOutModel, Depends(get_intern_user)],
    intern_service: Annotated[InternService, Depends()],
) -> list[TaskOutModel]:
    return await intern_service.get_tasks(user.user_id)


@router.get("/projects", tags=["Projects", "Dashboard"])
async def get_projects(
    user: Annotated[UserOutModel, Depends(get_intern_user)],
    intern_service: Annotated[InternService, Depends()],
) -> list[ProjectOutModel]:
    return await intern_service.get_projects(user.user_id)


@router.get("/todos", tags=["Todos", "Dashboard"])
async def get_intern_todos(
    user: Annotated[UserOutModel, Depends(get_intern_user)],
    todo_service: Annotated[TodoService, Depends()],
    limit: int | None = None,
    offset: int | None = None,
    done: bool | None = None,
) -> list[TodoOutModel]:
    todos = await todo_service.get_todo(user.user_id, done, limit, offset)
    return todos


@router.post("/todos", tags=["Todos", "Dashboard"], status_code=201)
async def create_intern_todo(
    todo_data: TodoInModel,
    user: Annotated[dict, Depends(get_intern_user)],
    todo_service: Annotated[TodoService, Depends()],
) -> TodoOutModel:
    return await todo_service.create_todo(user_id=user.get("sub"), todo_data=todo_data)


@router.patch("/todos/{todo_id}/complete", tags=["Todos", "Dashboard"])
async def complete_intern_todo(
    todo_id: UUID4,
    todo_service: Annotated[TodoService, Depends()],
    _: Annotated[dict, Depends(get_intern_user)],
) -> ORJSONResponse:
    await todo_service.complete_todo(todo_id)
    return ORJSONResponse({"message": "Todo marked as completed"}, status_code=200)
