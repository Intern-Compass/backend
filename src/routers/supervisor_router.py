from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Depends

from src.schemas.supervisor_schemas import SupervisorOutModel
from src.schemas.project_schemas import ProjectInModel, ProjectOutModel
from src.schemas.task_schemas import TaskInModel, TaskOutModel
from src.schemas.intern_schemas import InternOutModel
from src.services.matching_service import MatchingService
from src.services.supervisor_service import SupervisorService
from src.services.project_service import ProjectService
from src.services.task_service import TaskService
from src.utils import get_supervisor_user, get_intern_user

router: APIRouter = APIRouter(prefix="/supervisor", tags=["Supervisor"])

"""Router concerns everything that has to do with supervisors."""


@router.get("/my-interns")
async def get_interns(
    supervisor_service: Annotated[SupervisorService, Depends()],
    supervisor: Annotated[SupervisorOutModel, Depends(get_supervisor_user)],
):
    return await supervisor_service.get_interns(
        supervisor_id=UUID(supervisor.supervisor_id)
    )


@router.get("/display-matches", tags=["Matching"])
async def display_matches(
    matching_service: Annotated[MatchingService, Depends()],
):
    return await matching_service.display_matches()


@router.post("/perform-matching", tags=["Matching"])
async def perform_matches(
    matching_service: Annotated[MatchingService, Depends()],
):
    # Will refactor this to its own dedicated router.
    return await matching_service.perform_bulk_matching()


@router.post("/project", tags=["Project"])
async def create_new_project(
    project_service: Annotated[ProjectService, Depends()],    
    project_data: ProjectInModel     
) -> ProjectOutModel:      
    return await project_service.create_project(project_data=project_data)


@router.patch("/project-task", tags=["Project", "Task"])
async def add_task_to_project(
    project_service: Annotated[ProjectService, Depends()],    
    project_id: str,
    task_data: TaskInModel
) -> TaskOutModel:
    return await project_service.add_task_to_project(project_id=project_id, task_data=task_data)


@router.patch("/assign-task", tags=["Intern", "Task"])
async def assign_task_to_intern(
    task_service: Annotated[TaskService, Depends()],   
    intern_id: str,
    task_id: str    
) -> TaskOutModel:
    return await task_service.assign_task_to_intern(task_id=task_id, intern_id=intern_id)


@router.patch("/mark-task-as-completed", tags=["Task"])
async def mark_task_as_completed(
    task_service: Annotated[TaskService, Depends()],  
    task_id: str, 
    supervisor: Annotated[SupervisorOutModel, Depends(get_supervisor_user)],
    ) -> TaskOutModel:
    return await task_service.mark_task_as_completed(task_id=task_id, supervisor_id=supervisor.supervisor_id)