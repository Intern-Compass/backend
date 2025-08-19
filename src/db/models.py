from enum import StrEnum

from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Float,
    BigInteger,
    DateTime,
    Enum as SAEnum,
    func,
    ForeignKey,
)
from src.db import metadata, engine


class TaskPriority(StrEnum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


intern_table = Table(
    "intern",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("first_name", String(30)),
    Column("last_name", String(30)),
    Column("email", String(80)),
    Column("phone_number", String(15)),
    Column("desired_division", String(30)),
    Column("status", String),
    Column("supervisor_id", ForeignKey("supervisor.id"), nullable=True),
    Column("rating", Float, default=0.0),
    Column("created_at", DateTime, server_default=func.now()),
    Column("last_modified_at", DateTime, server_default=func.now()),
)

supervisor_table = Table(
    "supervisor",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("first_name", String(30)),
    Column("last_name", String(30)),
    Column("email", String(80)),
    Column("phone_number", String(15)),
    Column("division", String(30)),
    Column("status", String),
    Column("created_at", DateTime, server_default=func.now()),
    Column("last_modified_at", DateTime, server_default=func.now()),
)

"""
A milestone is to be set by the supervisor. 
It may be linked to any tasks they deem fit, and to any number of interns.
"""
milestone_table = Table(
    "milestone",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("title", String(30)),
    Column("description", String(100)),
    Column("created_at", DateTime, server_default=func.now()),
    Column("last_modified_at", DateTime, server_default=func.now()),
)


"""
A task is a record of work assigned by the supervisor to an intern.
"""
task_table = Table(
    "task",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("title", String(30)),
    Column("description", String(100)),
    Column("deadline", DateTime),
    Column("priority", SAEnum(TaskPriority)),
    Column("created_at", DateTime, server_default=func.now()),
    Column("last_modified_at", DateTime, server_default=func.now()),
)

note_table = Table(
    "note",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("title", String(30)),
    Column("content", String(150)),
    Column("intern_id", ForeignKey("intern.id")),
    Column("created_at", DateTime, server_default=func.now()),
    Column("last_modified_at", DateTime, server_default=func.now()),
)

association_milestone_task = Table(
    "assoc_milestone_task",
    metadata,
    Column("milestone_id", ForeignKey("milestone.id"), primary_key=True),
    Column("task_id", ForeignKey("task.id"), primary_key=True),
)

association_task_intern = Table(
    "assoc_task_intern",
    metadata,
    Column("task_id", ForeignKey("task.id"), primary_key=True),
    Column("intern_id", ForeignKey("intern.id"), primary_key=True),
    Column("completed_at", DateTime, nullable=True),
)

metadata.create_all(engine)
