from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from src.utils import get_intern_user

router: APIRouter = APIRouter(prefix="/intern", tags=["Intern"])

@router.get("/my-supervisor")
async def get_my_supervisor(
    intern_user: Annotated[dict, Depends(get_intern_user)],
):
    return intern_user