import uuid

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.app_models import Task, InternTask
from ..schemas.task_schemas import TaskInModel


class TaskRepository:
    def __init__(self):
        self.table = Task

    async def create_new_task(self, project_id: str, new_task: TaskInModel, conn: AsyncSession):
        task: Task = Task(
            project_id=uuid.UUID(project_id),
            title=new_task.title,
            description=new_task.description,
            due_date=new_task.due_date,
        )
        conn.add(task)
        return task

    async def get_task_by_id(self, conn: AsyncSession, id_value: str):
        stmt = select(self.table).where(self.table.id == uuid.UUID(id_value))
        result = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_tasks(self, conn: AsyncSession):
        stmt = select(self.table)
        result = await conn.execute(stmt)
        return result.scalars().all()

    async def get_all_tasks_by_intern_id(
        self, conn: AsyncSession, intern_id: uuid.UUID
    ):
        stmt = (
            select(self.table)
            .join(InternTask, self.table.id == InternTask.task_id)
            .where(InternTask.intern_id == intern_id)
        )
        result = await conn.execute(stmt)
        return result.scalars().all()

    async def get_all_tasks_by_project_id(self, conn: AsyncSession, project_id: str):
        stmt = select(self.table).where(self.table.project_id == uuid.UUID(project_id))
        result = await conn.execute(stmt)
        return result.scalars().all()

    async def update_task(self, conn: AsyncSession, id_value: str, values: dict):
        stmt = (
            update(self.table)
            .where(self.table.id == uuid.UUID(id_value))
            .values(**values)
            .returning(self.table)
        )
        result = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_task(self, conn: AsyncSession, id_value: str) -> None:
        stmt = delete(self.table).where(self.table.id == uuid.UUID(id_value))
        await conn.execute(stmt)
