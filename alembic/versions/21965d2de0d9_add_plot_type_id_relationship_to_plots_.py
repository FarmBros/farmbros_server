"""Add plot_type_id relationship to plots table

Revision ID: 21965d2de0d9
Revises: 7a713c51dccc
Create Date: 2025-10-07 21:48:48.608731

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21965d2de0d9'
down_revision: Union[str, Sequence[str], None] = '7a713c51dccc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add plot_type_id column to plots table
    op.add_column('plots', sa.Column('plot_type_id', sa.String(length=36), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove plot_type_id column from plots table
    op.drop_column('plots', 'plot_type_id')
