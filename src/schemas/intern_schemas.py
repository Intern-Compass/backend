from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, EmailStr

from .skill_schemas import SkillRes
from ..common import DepartmentEnum
from ..models import User
from ..models.app_models import Intern
from ..schemas import UserInModel, UserOutModel


class InternInModel(UserInModel):
    bio: str | None = None
    school: str
    internship_start_date: datetime
    internship_end_date: datetime


class BasicUserDetails(BaseModel):
    name: str
    email: Annotated[str, EmailStr]
    phone_number: str
    skills: str | None = None


class InternOutModel(UserOutModel):
    intern_id: Annotated[str, UUID]
    bio: str | None = None
    school: str | None = None
    internship_start_date: str
    internship_end_date: str

    @classmethod
    def from_intern(cls, user: User) -> "InternOutModel":
        return InternOutModel(
            user_id=str(user.id),
            firstname=user.firstname,
            lastname=user.lastname,
            phone_number=user.phone_number,
            email=user.email,
            type=user.type,
            department=DepartmentEnum(user.department_id),
            date_of_birth=user.date_of_birth.isoformat(),
            work_location=user.work_location,
            intern_id=str(user.intern.id),
            bio=user.intern.bio,
            school=user.intern.school,
            internship_start_date=user.intern.start_date.isoformat(),
            internship_end_date=user.intern.end_date.isoformat(),
        )

    @classmethod
    def from_model(cls, intern: Intern):
        return InternOutModel(
            user_id=str(intern.id),
            firstname=intern.user.firstname,
            lastname=intern.user.lastname,
            phone_number=intern.user.phone_number,
            email=intern.user.email,
            type=intern.user.type,
            department=DepartmentEnum(intern.user.department_id),
            date_of_birth=intern.user.date_of_birth.isoformat(),
            work_location=intern.user.work_location,
            intern_id=str(intern.id),
            bio=intern.bio,
            school=intern.school,
            internship_start_date=intern.start_date.isoformat(),
            internship_end_date=intern.end_date.isoformat(),
        )