from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from ..schemas.supervisor_schemas import SupervisorOutModel
from ..services.intern_service import InternService
from ..services.supervisor_service import SupervisorService
from ..utils import get_supervisor_user

router: APIRouter = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/interns/all/unmatched", tags=["Matching"])
async def get_all_unmatched_interns(
    intern_service: Annotated[InternService, Depends()],
    _: Annotated[SupervisorOutModel, Depends(get_supervisor_user)] # To use admin model once admin has been integrated
):
    """ Will be refactored to admin router"""
    return await intern_service.get_all_unmatched_interns()

@router.get("/interns/all")
async def get_all_interns(
        intern_service: Annotated[InternService, Depends()],
        _ : Annotated[SupervisorOutModel, Depends(get_supervisor_user)]
):
    return await intern_service.get_all_interns()

@router.get("/supervisors/all")
async def get_all_supervisors(
    _: Annotated[SupervisorOutModel, Depends(get_supervisor_user)],
    supervisor_service: Annotated[SupervisorService, Depends()]
):
    return await supervisor_service.get_supervisors()