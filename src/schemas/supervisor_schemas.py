from src.common import DepartmentEnum
from src.models import User
from src.models.app_models import Supervisor
from src.schemas import UserInModel, UserOutModel


class SupervisorInModel(UserInModel):
    position: str


class SupervisorOutModel(UserOutModel):
    supervisor_id: str
    position: str | None
    intern_count: int | None = None

    @classmethod
    def from_supervisor_user(cls, user: User) -> "SupervisorOutModel":
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

    @classmethod
    def from_model(cls, supervisor: Supervisor) -> "SupervisorOutModel":
        return SupervisorOutModel(
            user_id=str(supervisor.user.id),
            firstname=supervisor.user.firstname,
            lastname=supervisor.user.lastname,
            phone_number=supervisor.user.phone_number,
            email=supervisor.user.email,
            type=supervisor.user.type,
            department=DepartmentEnum(supervisor.user.department_id),
            date_of_birth=supervisor.user.date_of_birth.isoformat(),
            work_location=supervisor.user.work_location,
            supervisor_id=str(supervisor.id),
            position=supervisor.position,
            intern_count= len(supervisor.interns)
        )