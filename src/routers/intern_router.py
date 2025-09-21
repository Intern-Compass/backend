import uuid
from typing import Annotated
from uuid import UUID

from pydantic import UUID4

from fastapi import APIRouter
from fastapi.params import Depends

from ..schemas import UserOutModel
from ..schemas.intern_schemas import InternOutModel, BasicUserDetails
from ..schemas.project_schemas import ProjectOutModel
from ..schemas.task_schemas import TaskOutModel
from ..schemas.todo_schemas import TodoInModel, TodoOutModel
from ..services.intern_service import InternService
from ..services.todo_service import TodoService
from ..services.task_service import TaskService
from ..utils import get_intern_user, get_current_user, get_supervisor_user

from typing import List


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
    return await intern_service.get_intern_tasks(user_id=uuid.UUID(user.user_id))


@router.get("/projects", tags=["Project", "Dashboard"])
async def get_projects_assigned_to_by_supervisor(
    user: Annotated[InternOutModel, Depends(get_intern_user)],
    intern_service: Annotated[InternService, Depends()],
) -> list[ProjectOutModel]:
    return await intern_service.get_intern_projects(intern_id=uuid.UUID(user.intern_id))


@router.get("/todos", tags=["Todo", "Dashboard"])
async def get_intern_todos(
    user: Annotated[InternOutModel, Depends(get_intern_user)],
    todo_service: Annotated[TodoService, Depends()],
    is_done: bool | None = None,
) -> list[TodoOutModel]:
    todos = await todo_service.get_todos(user_id=UUID(user.user_id), is_done=is_done)
    return todos


@router.post("/todos", tags=["Todo", "Dashboard"])
async def create_intern_todo(
    todo_data: TodoInModel,
    user: Annotated[InternOutModel, Depends(get_intern_user)],
    todo_service: Annotated[TodoService, Depends()],
) -> TodoOutModel:
    return await todo_service.create_todo(
        user_id=UUID(user.user_id), todo_data=todo_data
    )


@router.patch("/todos/{todo_id}/complete", tags=["Todo", "Dashboard"])
async def complete_intern_todo(
    todo_id: UUID4,
    todo_service: Annotated[TodoService, Depends()],
    intern: Annotated[InternOutModel, Depends(get_intern_user)],
):
    return await todo_service.complete_todo(
        todo_id=todo_id, intern_id=UUID(intern.intern_id)
    )


@router.get("/all-tasks", tags=["Task"])
async def get_all_tasks(
    user: Annotated[InternOutModel, Depends(get_intern_user)],
    task_service: Annotated[TaskService, Depends()],
) -> List[TaskOutModel]:
    return await task_service.get_all_tasks_by_intern_id(intern_id=user.intern_id)


@router.get("/tasks")
async def get_tasks_by_project_id(
    project_id: str,
    user: Annotated[UserOutModel, Depends(get_current_user)],
    task_service: Annotated[TaskService, Depends()],
):
    return await task_service.get_all_tasks_by_project_id(project_id=UUID(project_id))
