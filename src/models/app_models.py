from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Optional, List
from uuid import uuid4
from zoneinfo import ZoneInfo

from sqlalchemy import String, Text, Date, DateTime, ForeignKey, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase

from ..common import UserType


class ReprMixin:
    def __repr__(self) -> str:
        """
        Automatically build a repr string from the model’s class name
        and its column attributes (like id, email, etc.).
        """
        values = []
        for col in getattr(self, "__repr_attrs__", []):
            value = getattr(self, col, None)
            values.append(f"{col}={value!r}")
        values_str = ", ".join(values)
        return f"<{self.__class__.__name__}({values_str})>"


class Base(DeclarativeBase, ReprMixin):
    pass


user_type_enum = Enum(UserType, name="usertype", create_type=True)


class User(Base):
    __tablename__ = "user"

    __repr_attrs__ = (
        "id",
        "email",
        "firstname",
        "lastname",
        "phone_number",
        "verified",
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    firstname: Mapped[str] = mapped_column(String(50))
    lastname: Mapped[str] = mapped_column(String(50))
    phone_number: Mapped[str] = mapped_column(String(15))
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    normalized_email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    date_of_birth: Mapped[datetime] = mapped_column(Date)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("department.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=False,
    )
    work_location: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now()
    )

    type: Mapped[UserType] = mapped_column(user_type_enum)
    verified: Mapped[bool] = mapped_column(default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
    )

    intern: Mapped[Intern] = relationship(
        "Intern", back_populates="user", uselist=False
    )
    supervisor: Mapped[Supervisor] = relationship(
        "Supervisor", back_populates="user", uselist=False
    )
    administrator: Mapped[Administrator] = relationship(
        "Administrator", back_populates="user", uselist=False
    )
    skills: Mapped[List[Skill]] = relationship(
        "Skill", secondary="user_skill", back_populates="users"
    )
    department: Mapped[Department] = relationship("Department", back_populates="users")
    verification_code: Mapped[Optional[VerificationCode]] = relationship(
        "VerificationCode", uselist=False, back_populates="user"
    )


class UserSkill(Base):
    __tablename__ = "user_skill"

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skill.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    note: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        Index("ix_user_skill_unique", "user_id", "skill_id", unique=True),
    )


class Intern(Base):
    __tablename__ = "intern"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        unique=True,
    )
    supervisor_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("supervisor.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    school: Mapped[str] = mapped_column(String, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)

    # relationships
    user: Mapped[User] = relationship("User", back_populates="intern")
    supervisor: Mapped[Supervisor] = relationship(
        "Supervisor", back_populates="interns"
    )
    skills: Mapped[List[Skill]] = association_proxy("user", "skills")
    tasks: Mapped[List[Task]] = relationship(
        "Task", secondary="intern_task", back_populates="interns"
    )
    notes: Mapped[List[Note]] = relationship("Note", back_populates="intern")


class InternTask(Base):
    __tablename__ = "intern_task"

    intern_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intern.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    task_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("task.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(ZoneInfo("UTC"))
    )

    __table_args__ = (
        Index("ix_intern_task_unique", "intern_id", "task_id", unique=True),
    )


class Supervisor(Base):
    __tablename__ = "supervisor"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        unique=True,
    )
    position: Mapped[Optional[str]] = mapped_column(String)

    user: Mapped[User] = relationship("User", back_populates="supervisor")
    interns: Mapped[List[Intern]] = relationship("Intern", back_populates="supervisor")
    projects: Mapped[List[Project]] = relationship(
        "Project", back_populates="supervisor"
    )
    skills: Mapped[List[Skill]] = association_proxy("user", "skills")
    tasks: Mapped[List[Task]] = relationship("Task", back_populates="supervisor")


class Administrator(Base):
    __tablename__ = "administrator"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
    )

    user: Mapped[User] = relationship("User", back_populates="administrator")


class Department(Base):
    __tablename__ = "department"

    id: Mapped[int] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # relationships
    users: Mapped[List[User]] = relationship("User", back_populates="department")
    projects: Mapped[List[Project]] = relationship(
        "Project", back_populates="department"
    )


class Skill(Base):
    __repr_attrs__ = (
        "id",
        "name"
    )

    __tablename__ = "skill"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String, unique=True)

    # relationships
    users: Mapped[List[User]] = relationship(
        "User", secondary="user_skill", back_populates="skills"
    )
    projects: Mapped[List[Project]] = relationship(
        "Project", secondary="project_skill", back_populates="skills"
    )


class Project(Base):
    __tablename__ = "project"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    title: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    supervisor_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("supervisor.id", onupdate="CASCADE", ondelete="SET NULL"),
    )
    department_id: Mapped[int] = mapped_column(
        ForeignKey("department.id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(ZoneInfo("UTC"))
    )

    # relationships
    skills: Mapped[List[Skill]] = relationship(
        "Skill", secondary="project_skill", back_populates="projects"
    )
    supervisor: Mapped[Optional[Supervisor]] = relationship(
        "Supervisor", back_populates="projects"
    )
    department: Mapped[Optional[Department]] = relationship(
        "Department", back_populates="projects"
    )
    tasks: Mapped[List[Task]] = relationship("Task", back_populates="project")
    milestones: Mapped[List[Milestone]] = relationship(
        "Milestone", back_populates="project"
    )


class ProjectIntern(Base):
    __tablename__ = "project_intern"

    intern_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intern.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(ZoneInfo("UTC"))
    )

    __table_args__ = (
        Index("ix_project_intern_unique", "intern_id", "project_id", unique=True),
    )


class ProjectSkill(Base):
    __tablename__ = "project_skill"

    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skill.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    __table_args__ = (
        Index("ix_project_skill_unique", "project_id", "skill_id", unique=True),
    )


class Task(Base):
    __tablename__ = "task"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project.id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    supervisor_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("supervisor.id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    title: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(ZoneInfo("UTC"))
    )

    project: Mapped[Project] = relationship("Project", back_populates="tasks")
    supervisor: Mapped[Supervisor] = relationship("Supervisor", back_populates="tasks")
    interns: Mapped[List[Intern]] = relationship(
        "Intern", secondary="intern_task", back_populates="tasks"
    )
    notes: Mapped[List[Note]] = relationship("Note", back_populates="task")


class Milestone(Base):
    __tablename__ = "milestone"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project.id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    title: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[Optional[str]] = mapped_column(String)

    project: Mapped[Project] = relationship("Project", back_populates="milestones")


class Note(Base):
    __tablename__ = "note"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    intern_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intern.id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    task_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("task.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
    )
    content: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(ZoneInfo("UTC"))
    )

    intern: Mapped[Intern] = relationship("Intern", back_populates="notes")
    task: Mapped[Optional[Task]] = relationship("Task", back_populates="notes")


class VerificationCode(Base):
    __tablename__ = "verification_code"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    value: Mapped[str] = mapped_column(String(6), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("UTC"))
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo("UTC")) + timedelta(minutes=10),
    )

    user: Mapped[User] = relationship("User", back_populates="verification_code")
