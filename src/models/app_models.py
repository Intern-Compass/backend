from __future__ import annotations

from uuid import uuid4
import uuid
from zoneinfo import ZoneInfo
from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import (
    String, Text, Date, DateTime, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    relationship, declarative_base, Mapped, mapped_column
)

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4())
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
    )

    intern: Mapped[Optional[Intern]] = relationship("Intern", back_populates="user", uselist=False)
    supervisor: Mapped[Optional[Supervisor]] = relationship("Supervisor", back_populates="user", uselist=False)
    administrator: Mapped[Optional[Administrator]] = relationship("Administrator", back_populates="user", uselist=False)
    created_skills: Mapped[List[Skill]] = relationship("Skill", back_populates="creator")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Division(Base):
    __tablename__ = "division"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    interns: Mapped[List[Intern]] = relationship("Intern", back_populates="division")
    supervisors: Mapped[List[Supervisor]] = relationship("Supervisor", back_populates="division")
    projects: Mapped[List[Project]] = relationship("Project", back_populates="division")


class Intern(Base):
    __tablename__ = "intern"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), unique=True)
    division_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("division.id"))
    name: Mapped[Optional[str]] = mapped_column(String)
    bio: Mapped[Optional[str]] = mapped_column(Text)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)

    user: Mapped[User] = relationship("User", back_populates="intern")
    division: Mapped[Optional[Division]] = relationship("Division", back_populates="interns")
    skills: Mapped[List[Skill]] = relationship("Skill", secondary="intern_skill", back_populates="interns")
    tasks: Mapped[List[Task]] = relationship("Task", secondary="intern_task", back_populates="interns")
    notes: Mapped[List[Note]] = relationship("Note", back_populates="intern")


class Supervisor(Base):
    __tablename__ = "supervisor"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), unique=True)
    division_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("division.id"))
    name: Mapped[Optional[str]] = mapped_column(String)
    position: Mapped[Optional[str]] = mapped_column(String)

    user: Mapped[User] = relationship("User", back_populates="supervisor")
    division: Mapped[Optional[Division]] = relationship("Division", back_populates="supervisors")
    projects: Mapped[List[Project]] = relationship("Project", back_populates="supervisor")
    skills: Mapped[List[Skill]] = relationship("Skill", secondary="supervisor_skill", back_populates="supervisors")


class Administrator(Base):
    __tablename__ = "administrator"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"), unique=True)
    name: Mapped[Optional[str]] = mapped_column(String)

    user: Mapped[User] = relationship("User", back_populates="administrator")


class Skill(Base):
    __tablename__ = "skill"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4())
    name: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_by_user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"))

    creator: Mapped[User] = relationship("User", back_populates="created_skills")
    interns: Mapped[List[Intern]] = relationship("Intern", secondary="intern_skill", back_populates="skills")
    tasks: Mapped[List[Task]] = relationship("Task", secondary="task_skill", back_populates="skills")
    supervisors: Mapped[List[Supervisor]] = relationship("Supervisor", secondary="supervisor_skill", back_populates="skills")


class InternSkill(Base):
    __tablename__ = "intern_skill"

    intern_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("intern.id"), primary_key=True)
    skill_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("skill.id"), primary_key=True)
    note: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (Index("ix_intern_skill_unique", "intern_id", "skill_id", unique=True),)


class Project(Base):
    __tablename__ = "project"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    supervisor_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("supervisor.id"))
    division_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("division.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(ZoneInfo("UTC")))

    supervisor: Mapped[Optional[Supervisor]] = relationship("Supervisor", back_populates="projects")
    division: Mapped[Optional[Division]] = relationship("Division", back_populates="projects")
    tasks: Mapped[List[Task]] = relationship("Task", back_populates="project")
    milestones: Mapped[List[Milestone]] = relationship("Milestone", back_populates="project")


class Task(Base):
    __tablename__ = "task"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("project.id"))
    title: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(ZoneInfo("UTC")))

    project: Mapped[Project] = relationship("Project", back_populates="tasks")
    skills: Mapped[List[Skill]] = relationship("Skill", secondary="task_skill", back_populates="tasks")
    interns: Mapped[List[Intern]] = relationship("Intern", secondary="intern_task", back_populates="tasks")
    notes: Mapped[List[Note]] = relationship("Note", back_populates="task")


class TaskSkill(Base):
    __tablename__ = "task_skill"

    task_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("task.id"), primary_key=True)
    skill_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("skill.id"), primary_key=True)

    __table_args__ = (Index("ix_task_skill_unique", "task_id", "skill_id", unique=True),)


class InternTask(Base):
    __tablename__ = "intern_task"

    intern_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("intern.id"), primary_key=True)
    task_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("task.id"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(ZoneInfo("UTC")))

    __table_args__ = (Index("ix_intern_task_unique", "intern_id", "task_id", unique=True),)


class Milestone(Base):
    __tablename__ = "milestone"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("project.id"))
    title: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped[Project] = relationship("Project", back_populates="milestones")


class Note(Base):
    __tablename__ = "note"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    intern_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("intern.id"))
    task_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("task.id"), nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(ZoneInfo("UTC")))

    intern: Mapped[Intern] = relationship("Intern", back_populates="notes")
    task: Mapped[Optional[Task]] = relationship("Task", back_populates="notes")


class SupervisorSkill(Base):
    __tablename__ = "supervisor_skill"

    supervisor_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("supervisor.id"), primary_key=True)
    skill_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("skill.id"), primary_key=True)
    note: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (Index("ix_supervisor_skill_unique", "supervisor_id", "skill_id", unique=True),)
