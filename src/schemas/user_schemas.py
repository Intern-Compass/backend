from datetime import datetime
from enum import Enum, unique
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from src.common import Department
from src.models import User


class UserInModel(BaseModel):
    firstname: str
    lastname: str
    phone_number: str
    email: str
    password: str
    date_of_birth: datetime
    department: Department
    work_location: str


class UserOutModel(BaseModel):
    id: str
    firstname: str
    lastname: str
    phone_number: str
    email: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_user(cls, user: User) -> "UserOutModel":
        return UserOutModel(
            id=str(user.id),
            firstname=user.firstname,
            lastname=user.lastname,
            phone_number=user.phone_number,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


@unique
class UserAccountTypeEmun(str, Enum):
    intern = "intern"
    supervisor = "supervisor"
    admin = "admin"
