"""Add crops table

Revision ID: 6484bfca6acf
Revises: 21965d2de0d9
Create Date: 2025-11-14 18:56:24.141488

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6484bfca6acf'
down_revision: Union[str, Sequence[str], None] = '21965d2de0d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create crops table with all fields."""
    # Create crops table with inline enum definitions
    # Alembic will handle enum creation automatically
    op.create_table(
        'crops',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('common_name', sa.String(length=255), nullable=False),
        sa.Column('genus', sa.String(length=100), nullable=True),
        sa.Column('species', sa.String(length=100), nullable=True),
        sa.Column('crop_group', sa.Enum(
            'fruit', 'vegetable', 'cereal', 'legume', 'root',
            'tuber', 'leafy_green', 'herb', 'flower', 'other',
            name='cropgroup'
        ), nullable=True),
        sa.Column('lifecycle', sa.Enum(
            'annual', 'perennial', 'biennial',
            name='lifecycle'
        ), nullable=True),
        sa.Column('germination_days', sa.Integer(), nullable=True),
        sa.Column('days_to_transplant', sa.Integer(), nullable=True),
        sa.Column('days_to_maturity', sa.Integer(), nullable=True),
        sa.Column('nitrogen_needs', sa.Float(), nullable=True),
        sa.Column('phosphorus_needs', sa.Float(), nullable=True),
        sa.Column('potassium_needs', sa.Float(), nullable=True),
        sa.Column('water_coefficient', sa.Float(), nullable=True),
        sa.Column('planting_methods', sa.Text(), nullable=True),
        sa.Column('planting_spacing_m', sa.Float(), nullable=True),
        sa.Column('row_spacing_m', sa.Float(), nullable=True),
        sa.Column('seedling_type', sa.Enum(
            'direct_seed', 'transplant', 'both',
            name='seedlingtype'
        ), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )

    # Create index on common_name for faster searches
    op.create_index(op.f('ix_crops_common_name'), 'crops', ['common_name'], unique=False)


def downgrade() -> None:
    """Drop crops table and enums."""
    op.drop_index(op.f('ix_crops_common_name'), table_name='crops')
    op.drop_table('crops')
    op.execute('DROP TYPE IF EXISTS seedlingtype')
    op.execute('DROP TYPE IF EXISTS lifecycle')
    op.execute('DROP TYPE IF EXISTS cropgroup')
