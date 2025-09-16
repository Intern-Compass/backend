from typing import Annotated
from uuid import UUID

from fastapi import BackgroundTasks, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

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
        
    async def create_project(self, project_data: ProjectInModel) -> ProjectOutModel:
        async with self.session.begin():            
            supervisor_id=UUID(self.supervisor.supervisor_id)
            if not self.supervisor:
                raise HTTPException(status_code=404, detail="Supervisor not found")
            project: Project = await self.project_repo.create_new_project(
                user_id=supervisor_id, project_data=project_data, conn=self.session
            )

        return ProjectOutModel(
            id=project.id,
            title=project.title,
            description=project.description,
            supervisor_id=project.supervisor_id,
            department_id=project.department_id,
            created_at=project.created_at
        )
        
        
    async def add_task_to_project(self, project_id: str, task_data: TaskInModel) -> TaskOutModel:
        async with self.session.begin():
            project = await self.project_repo.get_project_by_id(conn=self.session, id_value=project_id)            
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            #create new task
            task: Task = await self.task_repo.create_new_task(project_id=project.id, new_task=task_data, conn=self.session)
            
            #add task to project
            project.tasks.append(task)
            
            return TaskOutModel(
                id=str(task.id),
                project_id=str(task.project_id),
                title=task.title,
                description=task.description,
                is_completed=task.is_completed,
                is_submitted=task.is_submitted,  
                due_date=task.due_date,
                created_at=task.created_at,
            )
            
    
    
            
    
            
    