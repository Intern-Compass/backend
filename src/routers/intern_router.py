from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import ORJSONResponse

from src.schemas.intern_schemas import ISupervisor
from src.schemas.project_schemas import ProjectOutModel
from src.schemas.skill_schemas import SkillCreate
from src.schemas.task_schemas import TaskOutModel
from src.services.intern_service import InternService
from src.services.skill_service import SkillService
from src.utils import get_intern_user

router: APIRouter = APIRouter(prefix="/intern", tags=["Intern"])


# TODO: refactor to be used by a logged in user
@router.post("/skills", tags=["Skills"])
async def add_skills_to_intern(
    skills: list[SkillCreate],
    user: Annotated[dict, Depends(get_intern_user)],
    skill_service: Annotated[SkillService, Depends()],
) -> ORJSONResponse:
    """
    Attach skills to an intern.
    """
    await skill_service.add_skills_to_user(user_id=user.get("sub"), skills=skills)
    return ORJSONResponse({"message": "Skills added successfully"})


@router.get("/supervisor")
async def get_intern_supervisor(
    user: Annotated[dict, Depends(get_intern_user)],
    intern_service: Annotated[InternService, Depends()]
) -> ISupervisor:
    supervisor = await intern_service.get_supervisor(user.get("sub"))
    if supervisor:
        return supervisor
    return ORJSONResponse({"message": "Supervisor not found"}, status_code=404)


@router.get("/task", tags=["Tasks"])
async def get_intern_tasks(
    user: Annotated[dict, Depends(get_intern_user)],
    intern_service: Annotated[InternService, Depends()]
) -> list[TaskOutModel]:
    return await intern_service.get_tasks(user.get("sub"))


@router.get("/projects", tags=["Projects"])
async def get_projects(
    user: Annotated[dict, Depends(get_intern_user)],
    intern_service: Annotated[InternService, Depends()]
) -> list[ProjectOutModel]:
    return await intern_service.get_projects(user.get("sub"))
