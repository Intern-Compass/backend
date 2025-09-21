from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Depends

from ..schemas.supervisor_schemas import SupervisorOutModel
from ..services.supervisor_service import SupervisorService
from ..utils import get_supervisor_user

router: APIRouter = APIRouter(prefix="/supervisor", tags=["Supervisor"])

"""Router concerns everything that has to do with supervisors."""


@router.get("/my-interns")
async def get_interns(
    supervisor_service: Annotated[SupervisorService, Depends()],
    supervisor: Annotated[SupervisorOutModel, Depends(get_supervisor_user)],
):
    return await supervisor_service.get_interns(
        supervisor_id=UUID(supervisor.supervisor_id)
    )

