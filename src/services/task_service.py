from typing import Annotated
from uuid import UUID
import datetime

from fastapi import BackgroundTasks, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from ..db import get_db_session
from ..models.app_models import Project, Intern, Task
from ..repositories.project_repo import ProjectRepository
from ..repositories.task_repo import TaskRepository
from ..repositories.intern_repo import InternRepository
from ..repositories.general_user_repo import UserRepository
from ..repositories.supervisor_repo import SupervisorRepository
from ..schemas.project_schemas import ProjectOutModel, ProjectInModel
from ..schemas.task_schemas import TaskInModel, TaskOutModel
from ..schemas.supervisor_schemas import SupervisorOutModel
from src.utils import get_supervisor_user

class TaskService:
    def __init__(
        self, 
        intern_repo: Annotated[InternRepository, Depends()],
        project_repo: Annotated[ProjectRepository, Depends()],
        task_repo: Annotated[TaskRepository, Depends()],   
        session: Annotated[AsyncSession, Depends(get_db_session)],             
    ):
        self.intern_repo = intern_repo
        self.project_repo = project_repo
        self.task_repo = task_repo
        self.session = session
    
    async def assign_task_to_intern(self, task_id: str, intern_id: str):
        async with self.session.begin():
            task: Task | None = await self.task_repo.get_task_by_id(self, conn=self.session, id_value=task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            
            intern: Intern | None = await self.intern_repo.get_intern_by_id(self, conn=self.session, intern_id=intern_id)
            
            if not intern:
                raise HTTPException(status_code=404, detail="Intern not found")
            
            #asign task to intern
            intern.tasks.append(task)           
                        
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
        
   
    async def mark_task_as_completed(self, task_id: str, supervisor_id: str) -> TaskOutModel:
        async with self.session.begin():  
            task: Task | None = await self.task_repo.get_task_by_id(self, conn=self.session, id_value=task_id)
                                
            if not task.project or str(task.project.supervisor_id) != str(supervisor_id):
                raise HTTPException(
                    status_code=403,
                    detail="Supervisor not authorized to mark this task as completed"
                )
            
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")            
            
            if task.is_completed:
                raise HTTPException(status_code=400, detail="Task is already completed")            
            
            task.is_completed = True
            task.completed_at = datetime.utcnow()            
            
            updated_task = await self.task_repo.update_task(task)         
           
            return TaskOutModel(
                id=str(updated_task.id),
                project_id=str(updated_task.project_id),
                description=task.description,
                is_completed=task.is_completed,
                is_submitted=task.is_submitted,                
                due_date=task.due_date,
                created_at=task.created_at,
            )  
            
            
    async def submit_task(self, task_id: str, user_id: str) -> TaskOutModel:
        async with self.session.begin():
            task: Task | None = await self.task_repo.get_task_by_id(self, conn=self.session, id_value=task_id)
                        
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")     
            
            user = await self.intern_repo.get_intern_by_user_id(conn=self.session, user_id=user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            intern_ids = {intern.id for intern in task.interns}  
            if user_id not in intern_ids:
                raise HTTPException(status_code=403, detail="User not authorized to submit this task")
         
            if task.is_submitted:
                raise HTTPException(status_code=400, detail="Task is already submitted")
                        
            task.is_submitted = True
            task.submitted_at = datetime.utcnow()                          
                                 
            updated_task = await self.task_repo.update_task(task)         
           
            return TaskOutModel(
                id=str(updated_task.id),
                project_id=str(updated_task.project_id),
                description=task.description,
                is_completed=task.is_completed,
                is_submitted=task.is_submitted,                
                due_date=task.due_date,
                created_at=task.created_at,
            )  
    
    async def get_all_tasks_by_intern_id(self, intern_id: str) -> list[TaskOutModel]:
        async with self.session.begin():  
            return [
                TaskOutModel.from_model(task)
                for task in await self.task_repo.get_all_tasks_by_intern_id(conn=self.session, intern_id=UUID(intern_id))                 
            ]          
          
            
                         
            