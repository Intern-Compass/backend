from src.common import DepartmentEnum
from src.models import User
from src.models.app_models import Supervisor
from src.schemas import UserInModel, UserOutModel


class SupervisorInModel(UserInModel):
    position: str


class SupervisorOutModel(UserOutModel):
    supervisor_id: str
    position: str | None

    @classmethod
    def from_supervisor(cls, user: User) -> "SupervisorOutModel":
        return SupervisorOutModel(
            user_id=str(user.id),
            firstname=user.firstname,
            lastname=user.lastname,
            phone_number=user.phone_number,
            email=user.email,
            type=user.type,
            department=DepartmentEnum(user.department_id),
            date_of_birth=user.date_of_birth.isoformat(),
            work_location=user.work_location,
            supervisor_id=str(user.supervisor.id),
            position=user.supervisor.position,
        )
