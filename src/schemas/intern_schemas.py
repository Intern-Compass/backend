from datetime import datetime

from pydantic import BaseModel, EmailStr

from src.schemas import UserInModel


class InternInModel(UserInModel):
    bio: str | None = None
    school: str
    internship_start_date: datetime
    internship_end_date: datetime

class ISupervisor(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
