from typing import TypeVar, Sequence

from sqlalchemy import insert, select, update, delete, Select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.intern_model import (
    User, Intern, Supervisor, Administrator, Division,
    Skill, InternSkill, Project, Task, TaskSkill,
    InternTask, Milestone, Note, SupervisorSkill
)

T = TypeVar

class BaseRepository[T]:
    def __init__(self, table):
        self.table = table

    async def create(self, conn: AsyncSession, values: dict) -> T:
        stmt = insert(self.table).values(**values).returning(self.table)
        result = await conn.execute(stmt)
        return result.fetchone()

    async def get_by_id(self, conn: AsyncSession, id_value: str) -> T|None:
        stmt = select(self.table).where(self.table.c.id == id_value)
        result = await conn.execute(stmt)
        return result.fetchone()

    async def list_all(self, conn: AsyncSession) -> Sequence[T]:
        stmt = select(self.table)
        result = await conn.execute(stmt)
        return result.fetchall()

    async def update(self, conn: AsyncSession, id_value: str, values: dict) -> T:
        stmt = (
            update(self.table)
            .where(self.table.c.id == id_value)
            .values(**values)
            .returning(self.table)
        )
        result = await conn.execute(stmt)
        return result.fetchone()

    async def delete(self, conn: AsyncSession, id_value: str) -> None:
        stmt = delete(self.table).where(self.table.c.id == id_value)
        await conn.execute(stmt)


class InternRepository(BaseRepository):
    def __init__(self): super().__init__(Intern)

class SupervisorRepository(BaseRepository):
    def __init__(self): super().__init__(Supervisor)

class AdministratorRepository(BaseRepository):
    def __init__(self): super().__init__(Administrator)

class DivisionRepository(BaseRepository):
    def __init__(self): super().__init__(Division)

class SkillRepository(BaseRepository):
    def __init__(self): super().__init__(Skill)

class InternSkillRepository(BaseRepository):
    def __init__(self): super().__init__(InternSkill)

class ProjectRepository(BaseRepository):
    def __init__(self): super().__init__(Project)

class TaskRepository(BaseRepository):
    def __init__(self): super().__init__(Task)

class TaskSkillRepository(BaseRepository):
    def __init__(self): super().__init__(TaskSkill)

class InternTaskRepository(BaseRepository):
    def __init__(self): super().__init__(InternTask)

class MilestoneRepository(BaseRepository):
    def __init__(self): super().__init__(Milestone)

class NoteRepository(BaseRepository):
    def __init__(self): super().__init__(Note)

class SupervisorSkillRepository(BaseRepository):
    def __init__(self): super().__init__(SupervisorSkill)
