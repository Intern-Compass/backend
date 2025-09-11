"""
This module will handle:
    - Creation of accounts for intern
    - Viewing supervisor intern was assigned to
    - Viewing tasks assigned by the supervisor
    Anything else the intern_auth router might need
"""
from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db_session
from ..repositories.intern_repo import InternRepository


class InternService:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        intern_repo: Annotated[InternRepository, Depends()],
    ):
        self.session = session
        self.intern_repo = intern_repo

