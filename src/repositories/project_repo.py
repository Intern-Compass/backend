from sqlalchemy import Select, select, Result, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.app_models import Project, InternTask, Task
from src.schemas.project_schemas import ProjectInModel
from typing import Optional, List
from uuid import uuid4

class ProjectRepository:
    def __init__(self):
        self.table = Project

    async def create_new_project(self, new_project: ProjectInModel, conn: AsyncSession):
        
        project: Project = Project(
            title=new_project.title,
            description=new_project.description,
            supervisor_id=new_project.supervisor_id,
            division_id=new_project.division_id
        )
        conn.add(project)        
        await conn.refresh(project)
        return project
    
    async def get_project_by_id(self, conn: AsyncSession, id_value: str):
        stmt = select(self.table).where(self.table.id == id_value)
        result = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_projects(self, conn: AsyncSession):
        stmt = select(self.table)
        result = await conn.execute(stmt)
        return result.scalars().all()
    
    async def get_all_projects_by_intern_id(self, conn: AsyncSession, intern_id: str):
        stmt = (
        select(self.table)
        .join(Task, self.table.id == Task.project_id)
        .join(InternTask, Task.id == InternTask.task_id)
        .where(InternTask.intern_id == intern_id)
        .distinct()  
        )
        result = await conn.execute(stmt)
        return result.scalars().all()
    
    async def get_all_projects_by_supervisor_id(self, conn: AsyncSession, supervisor_id: str):
        stmt = select(self.table).where(self.table.supervisor_id == supervisor_id)
        result = await conn.execute(stmt)
        return result.scalars().all()

    async def update_project(self, conn: AsyncSession, id_value: str, values: dict):
        stmt = (
            update(self.table)
            .where(self.table.id == id_value)
            .values(**values)
            .returning(self.table)
        )
        result = await conn.execute(stmt)         
        return result.scalar_one_or_none()

    async def delete_project(self, conn: AsyncSession, id_value: str) -> None:
        stmt = delete(self.table).where(self.table.id == id_value)
        await conn.execute(stmt)
