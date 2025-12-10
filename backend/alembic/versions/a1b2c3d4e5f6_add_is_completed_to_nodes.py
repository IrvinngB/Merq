"""add_is_completed_to_nodes

Revision ID: a1b2c3d4e5f6
Revises: 3738d58efe26
Create Date: 2025-12-09 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '3738d58efe26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_completed column with default False
    op.add_column('roadmap_nodes', sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('roadmap_nodes', 'is_completed')
