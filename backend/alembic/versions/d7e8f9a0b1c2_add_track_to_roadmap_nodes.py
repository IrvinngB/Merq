"""add_track_to_roadmap_nodes

Revision ID: d7e8f9a0b1c2
Revises: a1b2c3d4e5f6
Create Date: 2026-03-19 13:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7e8f9a0b1c2'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'roadmap_nodes',
        sa.Column('track', sa.String(length=80), nullable=False, server_default='core')
    )


def downgrade() -> None:
    op.drop_column('roadmap_nodes', 'track')
