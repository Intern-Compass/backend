from datetime import datetime
from enum import Enum, unique, StrEnum

from pydantic import BaseModel

from src.common import Department, UserType
from src.models import User
from src.schemas.skill_schemas import SkillCreate

class UserInModel(BaseModel):
    firstname: str
    lastname: str
    phone_number: str
    email: str
    password: str
    skills: list[SkillCreate]
    date_of_birth: datetime
    department: Department
    work_location: str
    type: UserType


class UserOutModel(BaseModel):
    id: str
    firstname: str
    lastname: str
    phone_number: str
    email: str
    date_of_birth: str
    department: Department
    work_location: str
    type: UserType

    @classmethod
    def from_user(cls, user: User) -> "UserOutModel":
        return UserOutModel(
            id=str(user.id),
            firstname=user.firstname,
            lastname=user.lastname,
            phone_number=user.phone_number,
            email=user.email,
            type=user.type,
            department=user.division_name,
            date_of_birth=user.date_of_birth.isoformat(),
            work_location=user.work_location,
        )

