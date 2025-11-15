"""Add yield columns to crops table

Revision ID: 0235fb063a9a
Revises: 6484bfca6acf
Create Date: 2025-11-15 08:36:11.561938

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0235fb063a9a'
down_revision: Union[str, Sequence[str], None] = '6484bfca6acf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add yield columns to crops table."""
    op.add_column('crops', sa.Column('yield_per_plant', sa.Float(), nullable=True))
    op.add_column('crops', sa.Column('yield_per_area', sa.Float(), nullable=True))


def downgrade() -> None:
    """Remove yield columns from crops table."""
    op.drop_column('crops', 'yield_per_area')
    op.drop_column('crops', 'yield_per_plant')
