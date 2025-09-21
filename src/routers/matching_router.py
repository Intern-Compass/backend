from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Depends

from ..schemas.supervisor_schemas import SupervisorOutModel
from ..services.matching_service import MatchingService
from ..utils import get_supervisor_user

router: APIRouter = APIRouter(prefix="/matching", tags=["Matching", "Admin"])


@router.get("/display-matches")
async def display_matches(
    matching_service: Annotated[MatchingService, Depends()],
):
    return await matching_service.display_matches()


@router.post("/perform-matching",)
async def perform_matches(
    matching_service: Annotated[MatchingService, Depends()],
):
    # Will refactor this to its own dedicated router.
    return await matching_service.perform_bulk_matching()


@router.post("/assign-supervisor")
async def manually_assign_supervisor_to_intern(
    _: Annotated[SupervisorOutModel, Depends(get_supervisor_user)],
    matching_service: Annotated[MatchingService, Depends()],
    supervisor_id: str,
    intern_id: str
):
    return await matching_service.manually_match_supervisor_to_intern(
        supervisor_id=UUID(supervisor_id),
        intern_id=UUID(intern_id)
    )

@router.delete("/unassign-supervisor")
async def unassign_intern(
        _: Annotated[SupervisorOutModel, Depends(get_supervisor_user)],
        matching_service: Annotated[MatchingService, Depends()],
        intern_id: str
):
    return await matching_service.unmatch_supervisor_from_intern(
        intern_id=UUID(intern_id)
    )