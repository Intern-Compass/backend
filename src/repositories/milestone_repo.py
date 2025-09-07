from sqlalchemy import Select, select, Result, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.app_models import Milestone
from src.schemas.milestone_schemas import MilestoneInModel
from typing import Optional, List

class MilestoneRepository:
    def __init__(self):
        self.table = Milestone

    async def create_new_milestone(self, new_milestone: MilestoneInModel, conn: AsyncSession):
        milestone: Milestone = Milestone(
            project_id=new_milestone.project_id,
            title=new_milestone.title,
            description=new_milestone.description,
            due_date=new_milestone.due_date,
            status=new_milestone.status
        )
        conn.add(milestone)        
        await conn.refresh(milestone)
        return milestone
    
    async def get_milestone_by_id(self, conn: AsyncSession, id_value: str):
        stmt = select(self.table).where(self.table.id == id_value)
        result = await conn.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_milestones(self, conn: AsyncSession):
        stmt = select(self.table)
        result = await conn.execute(stmt)
        return result.scalars().all()
    
    async def get_all_milestones_by_project_id(self, conn: AsyncSession, project_id: str):
        stmt = select(self.table).where(self.table.project_id == project_id)
        result = await conn.execute(stmt)
        return result.scalars().all()

    async def update_milestone(self, conn: AsyncSession, id_value: str, values: dict):
        stmt = (
            update(self.table)
            .where(self.table.id == id_value)
            .values(**values)
            .returning(self.table)
        )
        result = await conn.execute(stmt)         
        return result.scalar_one_or_none()

    async def delete_milestone(self, conn: AsyncSession, id_value: str) -> None:
        stmt = delete(self.table).where(self.table.id == id_value)
        await conn.execute(stmt)          

