from datetime import datetime, date
from uuid import uuid4

from src.models.app_models import User, VerificationCode, Intern
from src.schemas import UserInModel, InternInModel
from src.common import Department

def create_mock_user(verified: bool = False) -> User:
    """Creates a mock User ORM object that matches the SQLAlchemy model."""
    user = User(
        id=uuid4(),
        firstname="Test",
        lastname="User",
        email="test@example.com",
        phone_number="1234567890",
        password="hashed_password",
        verified=verified,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    return user

def create_mock_intern(mock_user: User) -> Intern:
    """Creates a mock Intern ORM object that matches the SQLAlchemy model."""
    intern = Intern(
        id=uuid4(),
        user_id=mock_user.id,
        division_name=Department.IT.value,
        bio="A test intern bio.",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 9, 1),
        user=mock_user # Set up the ORM relationship
    )
    return intern

def create_user_in_model() -> UserInModel:
    """Creates a user input schema object."""
    return UserInModel(
        firstname="Test",
        lastname="User",
        phone_number="1234567890",
        email="test@example.com",
        password="plain_password",
        date_of_birth=datetime(2000, 1, 1),
        department=Department.INFORMATION_TECHNOLOGY,
        work_location="Remote"
    )

def create_intern_in_model() -> InternInModel:
    """Creates an intern input schema object."""
    return InternInModel(
        firstname="Test",
        lastname="Intern",
        phone_number="0987654321",
        email="intern@example.com",
        password="plain_password",
        date_of_birth=datetime(2002, 5, 10),
        department=Department.INFORMATION_TECHNOLOGY,
        work_location="Office",
        bio="Eager to learn!",
        school="University of Testing",
        internship_start_date=datetime(2025, 6, 1),
        internship_end_date=datetime(2025, 9, 1)
    )

def create_mock_verification_code(user_id=None) -> VerificationCode:
    """Creates a mock VerificationCode ORM object."""
    return VerificationCode(
        id=uuid4(),
        user_id=user_id or uuid4(),
        value="123456"
    )

