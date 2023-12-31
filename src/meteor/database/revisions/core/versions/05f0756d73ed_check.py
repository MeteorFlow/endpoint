"""Check

Revision ID: 05f0756d73ed
Revises: 4f23fe5f7582
Create Date: 2024-01-01 02:51:04.926999

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05f0756d73ed'
down_revision: Union[str, None] = '4f23fe5f7582'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
