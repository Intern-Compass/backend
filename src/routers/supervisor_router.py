from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from src.services.matching_service import MatchingService
from src.services.supervisor_service import SupervisorService
from src.utils import get_supervisor_user

router: APIRouter = APIRouter(prefix="/supervisor", tags=["Supervisor"])

"""Router concerns everything that has to do with supervisors."""


@router.get("/my-interns")
async def get_interns(
    supervisor_service: Annotated[SupervisorService, Depends()],
    supervisor: Annotated[dict, Depends(get_supervisor_user)],
):
    return await supervisor_service.get_interns(
        supervisor_id=supervisor.get("supervisor_id")
    )


@router.post("/perform-matching")
async def perform_matches(
    matching_service: Annotated[MatchingService, Depends()],
    _: Annotated[dict, Depends(get_supervisor_user)],
):
    # Will refactor this to its own dedicated router.
    return await matching_service.perform_bulk_matching()
