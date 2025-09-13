"""merge heads

Revision ID: 40a7cb35f41e
Revises: 64e02abcf18e, 8cb3c8f82bb3
Create Date: 2025-09-12 23:52:22.528405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40a7cb35f41e'
down_revision: Union[str, Sequence[str], None] = ('64e02abcf18e', '8cb3c8f82bb3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
