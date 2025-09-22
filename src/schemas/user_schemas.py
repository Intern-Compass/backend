import re
from datetime import datetime, date
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator

from src.common import DepartmentEnum, UserType
from src.models import User
from src.schemas.skill_schemas import SkillCreate

PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&.])[A-Za-z\d@$!%*?&.]{8,}$"
)

class UserInModel(BaseModel):
    firstname: str
    lastname: str
    phone_number: str
    email: Annotated[str, EmailStr]
    password: str
    skills: list[SkillCreate]
    date_of_birth: date
    department: DepartmentEnum
    work_location: str
    type: UserType | None = None

    @field_validator("password")
    def validate_password(cls, v: str) -> str:
        if not PASSWORD_PATTERN.match(v):
            raise ValueError(
                "Password must be at least 8 characters, include uppercase, "
                "lowercase, number, and special character"
            )
        return v

class UserOutModel(BaseModel):
    user_id: Annotated[str, UUID]
    firstname: str
    lastname: str
    phone_number: str
    email: str
    date_of_birth: str
    department: DepartmentEnum
    work_location: str
    type: UserType

    class Config:
        use_enum_values = True

    @classmethod
    def from_user(cls, user: User) -> "UserOutModel":
        return UserOutModel(
            user_id=str(user.id),
            firstname=user.firstname,
            lastname=user.lastname,
            phone_number=user.phone_number,
            email=user.email,
            type=user.type,
            department=DepartmentEnum(user.department_id),
            date_of_birth=user.date_of_birth.isoformat(),
            work_location=user.work_location,
        )


class ResetPasswordRequest(BaseModel):
    token: str
    password: str

    @field_validator("password")
    def validate_password(cls, v: str) -> str:
        if not PASSWORD_PATTERN.match(v):
            raise ValueError(
                "Password must be at least 8 characters, include uppercase, "
                "lowercase, number, and special character"
            )
        return v


class UserEmail(BaseModel):
    email: Annotated[str, EmailStr]


class VerificationCode(BaseModel):
    code: str
