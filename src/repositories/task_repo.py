from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.app_models import Task, InternTask
from ..schemas.task_schemas import TaskInModel


class TaskRepository:
    def __init__(self):
        self.table = Task

    async def create_new_task(self, project_id: UUID, supervisor_id: UUID, new_task: TaskInModel, conn: AsyncSession):
        task: Task = self.table(
            project_id=project_id,
            title=new_task.title,
            description=new_task.description,
            supervisor_id=supervisor_id,
            due_date=new_task.due_date,
        )
        conn.add(task)
        await conn.flush()
        await conn.refresh(task)
        return task

    async def get_task_by_id(self, conn: AsyncSession, id_value: UUID):
        stmt = select(self.table).where(self.table.id == id_value)
        result = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_tasks(self, conn: AsyncSession):
        stmt = select(self.table)
        result = await conn.execute(stmt)
        return result.scalars().all()

    async def get_all_tasks_by_intern_id(
        self, conn: AsyncSession, intern_id: UUID
    ):
        stmt = (
            select(self.table)
            .join(InternTask, self.table.id == InternTask.task_id)
            .where(InternTask.intern_id == intern_id)
        )
        result = await conn.execute(stmt)
        return result.scalars().all()

    async def get_all_tasks_by_project_id(self, conn: AsyncSession, project_id: UUID):
        stmt = select(self.table).where(self.table.project_id == project_id)
        result = await conn.execute(stmt)
        return result.scalars().all()

    async def update_task(self, conn: AsyncSession, task_id: UUID, values: dict):
        stmt = (
            update(self.table)
            .where(self.table.id == task_id)
            .values(**values)
            .returning(self.table)
        )
        result = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_task(self, conn: AsyncSession, task_id: UUID) -> None:
        stmt = delete(self.table).where(self.table.id == task_id)
        await conn.execute(stmt)
