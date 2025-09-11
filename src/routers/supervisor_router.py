from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from src.services.supervisor_service import SupervisorService
from src.utils import get_supervisor_user

router: APIRouter = APIRouter(prefix="/supervisor", tags=["Supervisor"])

"""Router concerns everything that has to do with supervisors."""

@router.get("/my-interns")
async def get_interns(
    supervisor_service: Annotated[SupervisorService, Depends()],
    supervisor: Annotated[dict, Depends(get_supervisor_user)],
):
    return await supervisor_service.get_interns(supervisor_id=supervisor.get("supervisor_id"))

@router.get("/assign-intern")
async def assign_intern(
    intern_id: str,
    supervisor_service: Annotated[SupervisorService, Depends()],
    supervisor: Annotated[dict, Depends(get_supervisor_user)],
):
    return await supervisor_service.assign_intern_to_supervisor(
        supervisor_id=supervisor.get("supervisor_id"), intern_id=intern_id
    )