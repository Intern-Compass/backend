from datetime import datetime

from src.schemas import UserInModel


class InternInModel(UserInModel):
    bio: str | None = None
    school: str
    internship_start_date: datetime
    internship_end_date: datetime
