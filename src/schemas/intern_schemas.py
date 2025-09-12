from datetime import datetime, date

from src.common import DepartmentEnum
from src.models import User
from src.schemas import UserInModel, UserOutModel


class InternInModel(UserInModel):
    bio: str | None = None
    school: str
    internship_start_date: datetime
    internship_end_date: datetime


class InternOutModel(UserOutModel):
    intern_id: str
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
