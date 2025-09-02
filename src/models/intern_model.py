from sqlalchemy import (
    Table, Column, String, Text, Date, DateTime, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID
import datetime

from ..db import metadata

User = Table(
    "user", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("email", String, nullable=False, unique=True),
    Column("password_hash", String, nullable=False),
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow),
)

Division = Table(
    "division", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", String, nullable=False, unique=True),
    Column("description", Text),
)

Intern = Table(
    "intern", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("user.id"), unique=True),
    Column("division_id", UUID(as_uuid=True), ForeignKey("division.id")),
    Column("name", String),
    Column("bio", Text),
    Column("start_date", Date),
    Column("end_date", Date),
)

Supervisor = Table(
    "supervisor", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("user.id"), unique=True),
    Column("division_id", UUID(as_uuid=True), ForeignKey("division.id")),
    Column("name", String),
    Column("position", String),
)

Administrator = Table(
    "administrator", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("user.id"), unique=True),
    Column("name", String),
)

Skill = Table(
    "skill", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", String, unique=True),
    Column("description", Text),
    Column("created_by_user_id", UUID(as_uuid=True), ForeignKey("user.id")),
)

InternSkill = Table(
    "intern_skill", metadata,
    Column("intern_id", UUID(as_uuid=True), ForeignKey("intern.id")),
    Column("skill_id", UUID(as_uuid=True), ForeignKey("skill.id")),
    Column("note", Text),
    Index("ix_intern_skill_unique", "intern_id", "skill_id", unique=True)
)

Project = Table(
    "project", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("title", String),
    Column("description", Text),
    Column("supervisor_id", UUID(as_uuid=True), ForeignKey("supervisor.id")),
    Column("division_id", UUID(as_uuid=True), ForeignKey("division.id")),
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
)

Task = Table(
    "task", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("project_id", UUID(as_uuid=True), ForeignKey("project.id")),
    Column("title", String),
    Column("description", Text),
    Column("due_date", Date),
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
)

TaskSkill = Table(
    "task_skill", metadata,
    Column("task_id", UUID(as_uuid=True), ForeignKey("task.id")),
    Column("skill_id", UUID(as_uuid=True), ForeignKey("skill.id")),
    Index("ix_task_skill_unique", "task_id", "skill_id", unique=True)
)

InternTask = Table(
    "intern_task", metadata,
    Column("intern_id", UUID(as_uuid=True), ForeignKey("intern.id")),
    Column("task_id", UUID(as_uuid=True), ForeignKey("task.id")),
    Column("assigned_at", DateTime, default=datetime.datetime.utcnow),
    Index("ix_intern_task_unique", "intern_id", "task_id", unique=True)
)

Milestone = Table(
    "milestone", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("project_id", UUID(as_uuid=True), ForeignKey("project.id")),
    Column("title", String),
    Column("description", Text),
    Column("due_date", Date),
    Column("status", String),
)

Note = Table(
    "note", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("intern_id", UUID(as_uuid=True), ForeignKey("intern.id")),
    Column("task_id", UUID(as_uuid=True), ForeignKey("task.id"), nullable=True),
    Column("content", Text),
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
)

SupervisorSkill = Table(
    "supervisor_skill", metadata,
    Column("supervisor_id", UUID(as_uuid=True), ForeignKey("supervisor.id")),
    Column("skill_id", UUID(as_uuid=True), ForeignKey("skill.id")),
    Column("note", Text),
    Index("ix_supervisor_skill_unique", "supervisor_id", "skill_id", unique=True)
)
