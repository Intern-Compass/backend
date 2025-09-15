"""Utilities for our Tests"""

from datetime import datetime, date
from unittest.mock import MagicMock
from uuid import UUID, uuid4

from src.models.app_models import Supervisor, User, VerificationCode, Intern
from src.schemas.supervisor_schemas import SupervisorInModel
from src.schemas.user_schemas import UserInModel
from src.schemas.intern_schemas import InternInModel
from src.common import DepartmentEnum, UserType
from src.schemas.skill_schemas import SkillCreate
from src.utils import normalize_string


def create_mock_user(
    verified: bool, user_type: UserType = UserType.INTERN
) -> MagicMock:
    mock_user = MagicMock(spec=User)
    user_email = "test@example.com"

    mock_user.id = uuid4()
    mock_user.firstname = "Test"
    mock_user.lastname = "User"
    mock_user.phone_number = "1234567890"
    mock_user.email = user_email
    mock_user.normalized_email = normalize_string(user_email)
    mock_user.password = "hashed_password"
    mock_user.work_location = "Remote"
    mock_user.verified = verified
    mock_user.type = user_type

    mock_user.date_of_birth = date(2000, 1, 1)
    mock_user.department_id = DepartmentEnum.INFORMATION_TECHNOLOGY.value
    mock_user.created_at = datetime.now()
    mock_user.updated_at = datetime.now()

    return mock_user


def create_mock_intern(mock_user: User) -> User:
    mock_intern = MagicMock(spec=Intern)
    mock_intern.id = uuid4()
    mock_intern.user_id = mock_user.id
    mock_intern.bio = "A test intern bio."
    mock_intern.school = "Unilag"
    mock_intern.start_date = date(2025, 6, 1)
    mock_intern.end_date = date(2025, 9, 1)
    mock_intern.user = mock_user

    mock_user.intern = mock_intern
    return mock_user


def create_mock_supervisor(mock_user: User) -> Supervisor:
    mock_supervisor = MagicMock(spec=Supervisor)
    mock_supervisor.id = uuid4()
    mock_supervisor.user_id = mock_user.id
    mock_supervisor.position = "Manager Emerging Technologies"
    mock_supervisor.user = mock_user

    mock_user.supervisor = mock_supervisor
    return mock_user


def create_user_in_model() -> UserInModel:
    return UserInModel(
        firstname="Test",
        lastname="User",
        phone_number="1234567890",
        email="test@example.com",
        password="strongpassword123",
        skills=[SkillCreate(name="Python"), SkillCreate(name="FastAPI")],
        date_of_birth=datetime(2000, 1, 1),
        department=DepartmentEnum.INFORMATION_TECHNOLOGY,
        work_location="Remote",
    )


def create_intern_in_model() -> InternInModel:
    return InternInModel(
        firstname="Test",
        lastname="User",
        phone_number="1234567890",
        email="test@example.com",
        password="strongpassword123",
        skills=[SkillCreate(name="Python"), SkillCreate(name="FastAPI")],
        date_of_birth=datetime(2000, 1, 1),
        department=DepartmentEnum.INFORMATION_TECHNOLOGY,
        work_location="Remote",
        bio="developer",
        school="Unilag",
        internship_start_date=datetime.now(),
        internship_end_date=datetime.now(),
    )


def create_supervisor_in_model() -> SupervisorInModel:
    return SupervisorInModel(
        firstname="Test",
        lastname="User",
        phone_number="1234567890",
        email="test@example.com",
        password="strongpassword123",
        skills=[SkillCreate(name="Python"), SkillCreate(name="FastAPI")],
        date_of_birth=datetime(2000, 1, 1),
        department=DepartmentEnum.INFORMATION_TECHNOLOGY,
        work_location="Remote",
        position="Manager Emerging Technologies",
    )


def create_mock_verification_code(user_id: UUID) -> VerificationCode:
    return VerificationCode(id=uuid4(), user_id=user_id or uuid4(), value="123456")
