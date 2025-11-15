"""Add planted_crop table

Revision ID: 37a9fcd39324
Revises: 0235fb063a9a
Create Date: 2025-11-15 08:55:38.105720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37a9fcd39324'
down_revision: Union[str, Sequence[str], None] = '0235fb063a9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create planted_crop table."""
    op.create_table('planted_crop',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('crop_id', sa.Integer(), nullable=False),
        sa.Column('plot_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('planting_method', sa.String(length=100), nullable=True),
        sa.Column('planting_spacing', sa.Float(), nullable=True),
        sa.Column('germination_date', sa.DateTime(), nullable=True),
        sa.Column('transplant_date', sa.DateTime(), nullable=True),
        sa.Column('seedling_age', sa.Integer(), nullable=True),
        sa.Column('harvest_date', sa.DateTime(), nullable=True),
        sa.Column('number_of_crops', sa.Integer(), nullable=True),
        sa.Column('estimated_yield', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['crop_id'], ['crops.id'], ),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )


def downgrade() -> None:
    """Drop planted_crop table."""
    op.drop_table('planted_crop')
