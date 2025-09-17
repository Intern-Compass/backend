from typing import Annotated
from uuid import UUID

from fastapi import BackgroundTasks, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN

from ..db import get_db_session
from ..models.app_models import Project, Supervisor, Task
from ..repositories.project_repo import ProjectRepository
from ..repositories.task_repo import TaskRepository
from ..repositories.general_user_repo import UserRepository
from ..repositories.supervisor_repo import SupervisorRepository
from ..schemas.project_schemas import ProjectOutModel, ProjectInModel
from ..schemas.task_schemas import TaskInModel, TaskOutModel
from ..schemas.supervisor_schemas import SupervisorOutModel
from src.utils import get_supervisor_user

class ProjectService:
    def __init__(
        self,
        project_repo: Annotated[ProjectRepository, Depends()],        
        task_repo: Annotated[TaskRepository, Depends()],
        supervisor_repo: Annotated[SupervisorRepository, Depends()],          
        user_repo: Annotated[UserRepository, Depends()],
        background_tasks: BackgroundTasks,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        supervisor: Annotated[SupervisorOutModel, Depends(get_supervisor_user)],
    ):
        self.project_repo = project_repo
        self.task_repo = task_repo
        self.supervisor_repo = supervisor_repo
        self.user_repo = user_repo
        self.background_tasks = background_tasks
        self.session = session
        self.supervisor = supervisor
        
    async def create_project(self, project_data: ProjectInModel, supervisor_id: UUID) -> ProjectOutModel:
        async with self.session.begin():
            supervisor: Supervisor | None = await self.supervisor_repo.get_supervisor_details(
                conn=self.session, supervisor_id=supervisor_id
            )
            if not supervisor:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND, detail="Supervisor not found"
                )

            project: Project = await self.project_repo.create_new_project(
                supervisor_id=supervisor_id,
                department_id=supervisor.user.department_id,
                new_project=project_data,
                conn=self.session
            )

            return ProjectOutModel.from_model(project=project)
        
        
    async def add_task_to_project(
            self,
            project_id: UUID,
            supervisor_id: UUID,
            task_data: TaskInModel
    ) -> TaskOutModel:
        async with self.session.begin():
            project: Project | None = await self.project_repo.get_project_by_id(conn=self.session, project_id=project_id)
            if not project:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Project not found")

            if project.supervisor_id != supervisor_id:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Supervisor not authorized to add task to this project"
                )
            # Create new task
            task: Task = await self.task_repo.create_new_task(
                project_id=project.id,
                new_task=task_data,
                conn=self.session,
                supervisor_id=supervisor_id
            )
            
            return TaskOutModel.from_model(task=task)

    async def get_tasks_by_project_id(self, project_id: UUID, supervisor_id: UUID) -> list[TaskOutModel]:
        async with self.session.begin():
            project: Project = await self.project_repo.get_project_by_id(
                conn=self.session, project_id=project_id,
            )
            if project.supervisor_id != supervisor_id:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Supervisor not authorized to view this project"
                )

            return [TaskOutModel.from_model(task) for task in project.tasks]

    async def get_all_projects_created_by_supervisor(self, supervisor_id: UUID):
        async with self.session.begin():
            projects: list[Project] = await self.project_repo.get_all_projects_by_supervisor_id(
                conn=self.session, supervisor_id=supervisor_id
            )

            return [ProjectOutModel.from_model(project) for project in projects]



    
            
    
            
    