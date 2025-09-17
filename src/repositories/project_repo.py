from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.app_models import Project, InternTask, Task
from ..schemas.project_schemas import ProjectInModel


class ProjectRepository:
    def __init__(self):
        self.table = Project

    async def create_new_project(
        self,
        supervisor_id: UUID,
        department_id: int,
        new_project: ProjectInModel,
        conn: AsyncSession,
    ):
        project: Project = self.table(
            title=new_project.title,
            description=new_project.description,
            supervisor_id=supervisor_id,
            department_id=department_id,
        )
        conn.add(project)
        await conn.flush()
        await conn.refresh(project)
        return project

    async def get_project_by_id(self, conn: AsyncSession, project_id: UUID):
        stmt = (
            select(self.table)
            .where(self.table.id == project_id)
            .options(selectinload(Project.tasks))
        )
        result = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_projects(self, conn: AsyncSession):
        stmt = select(self.table)
        result = await conn.execute(stmt)
        return result.scalars().all()

    async def get_all_projects_by_intern_id(self, conn: AsyncSession, intern_id: UUID):
        stmt = (
            select(self.table)
            .join(Task, self.table.id == Task.project_id)
            .join(InternTask, Task.id == InternTask.task_id)
            .where(InternTask.intern_id == intern_id)
            .distinct()
        )
        result = await conn.execute(stmt)
        return result.scalars().all()

    async def get_all_projects_by_supervisor_id(
        self, conn: AsyncSession, supervisor_id: UUID
    ):
        stmt = select(self.table).where(self.table.supervisor_id == supervisor_id)
        result = await conn.execute(stmt)
        return result.scalars().all()

    async def update_project(self, conn: AsyncSession, project_id: str, values: dict):
        stmt = (
            update(self.table)
            .where(self.table.id == UUID(project_id))
            .values(**values)
            .returning(self.table)
        )
        result = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_project(self, conn: AsyncSession, project_id: str) -> None:
        stmt = delete(self.table).where(self.table.id == UUID(project_id))
        await conn.execute(stmt)
