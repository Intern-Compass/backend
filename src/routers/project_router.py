from fastapi import APIRouter, Depends
from typing import Annotated
from uuid import UUID

from ..schemas.project_schemas import ProjectInModel, ProjectOutModel
from ..schemas.supervisor_schemas import SupervisorOutModel
from ..schemas.task_schemas import TaskInModel,  TaskOutModel
from ..services.project_service import ProjectService
from ..services.task_service import TaskService
from ..utils import get_supervisor_user

router: APIRouter = APIRouter(prefix="/project", tags=["Project"])

@router.post("/", tags=["Supervisor", "Project"])
async def create_new_project(
    project_service: Annotated[ProjectService, Depends()],
    supervisor: Annotated[SupervisorOutModel, Depends(get_supervisor_user)],
    project_data: ProjectInModel
) -> ProjectOutModel:
    return await project_service.create_project(
        project_data=project_data, supervisor_id=UUID(supervisor.supervisor_id)
    )

@router.get("/", tags=["Supervisor", "Project"])
async def get_all_projects_created_by_supervisor(
    project_service: Annotated[ProjectService, Depends()],
    supervisor: Annotated[SupervisorOutModel, Depends(get_supervisor_user)],
) -> list[ProjectOutModel]:
    return await project_service.get_all_projects_created_by_supervisor(
        supervisor_id=UUID(supervisor.supervisor_id)
    )

@router.post("/{project_id}/task", tags=["Supervisor", "Project", "Task"])
async def add_task_to_project(
    project_service: Annotated[ProjectService, Depends()],
    supervisor: Annotated[SupervisorOutModel, Depends(get_supervisor_user)],
    task_data: TaskInModel,
    project_id: str,
) -> TaskOutModel:
    return await project_service.add_task_to_project(
        project_id=UUID(project_id),
        supervisor_id=UUID(supervisor.supervisor_id),
        task_data=task_data
    )

@router.get("/{project_id}/tasks", tags=["Supervisor", "Project", "Task"])
async def get_tasks_by_project_id(
    project_service: Annotated[ProjectService, Depends()],
    supervisor: Annotated[SupervisorOutModel, Depends(get_supervisor_user)],
    project_id: str,
):
    return await project_service.get_tasks_by_project_id(
        project_id=UUID(project_id),
        supervisor_id=UUID(supervisor.supervisor_id)
    )

@router.patch("/assign-task", tags=["Supervisor", "Task"])
async def assign_task_to_intern(
    task_service: Annotated[TaskService, Depends()],
    supervisor: Annotated[SupervisorOutModel, Depends(get_supervisor_user)],
    intern_id: str,
    task_id: str
) -> TaskOutModel:
    return await task_service.assign_task_to_intern(
        task_id=UUID(task_id),
        intern_id=UUID(intern_id),
        supervisor_id=UUID(supervisor.supervisor_id)
    )

@router.get("/task/submissions", tags=["Supervisor", "Task"])
async def get_task_submissions(
    task_service: Annotated[TaskService, Depends()],
    supervisor: Annotated[SupervisorOutModel, Depends(get_supervisor_user)],
    task_id: str,
) -> list[TaskOutModel]:
    pass


@router.patch("/mark-task-as-completed", tags=["Supervisor", "Task"])
async def mark_task_as_completed(
    task_service: Annotated[TaskService, Depends()],
    task_id: str,
    supervisor: Annotated[SupervisorOutModel, Depends(get_supervisor_user)],
    ) -> TaskOutModel:
    return await task_service.mark_task_as_completed(task_id=task_id, supervisor_id=supervisor.supervisor_id)

