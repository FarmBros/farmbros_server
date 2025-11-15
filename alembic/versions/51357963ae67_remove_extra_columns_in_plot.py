"""remove extra columns in plot

Revision ID: 51357963ae67
Revises: 0e701b860cf4
Create Date: 2025-10-06 20:33:34.627696

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '51357963ae67'
down_revision: Union[str, Sequence[str], None] = '0e701b860cf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove extra columns from plots table that are not needed."""
    # Remove unnecessary columns from plots table
    op.drop_column('plots', 'status')
    op.drop_column('plots', 'elevation')
    op.drop_column('plots', 'slope')
    op.drop_column('plots', 'soil_type')
    op.drop_column('plots', 'ph_level')
    op.drop_column('plots', 'nitrogen_level')
    op.drop_column('plots', 'phosphorus_level')
    op.drop_column('plots', 'potassium_level')
    op.drop_column('plots', 'organic_matter')
    op.drop_column('plots', 'current_crop')
    op.drop_column('plots', 'crop_variety')
    op.drop_column('plots', 'planting_date')
    op.drop_column('plots', 'expected_harvest_date')
    op.drop_column('plots', 'last_harvest_date')
    op.drop_column('plots', 'livestock_type')
    op.drop_column('plots', 'livestock_count')
    op.drop_column('plots', 'grazing_capacity')
    op.drop_column('plots', 'irrigation_type')
    op.drop_column('plots', 'water_source')


def downgrade() -> None:
    """Add back the extra columns to plots table."""
    # Add back the removed columns to plots table
    op.add_column('plots', sa.Column('status', postgresql.ENUM('ACTIVE', 'FALLOW', 'PREPARING', 'HARVESTED', 'MAINTENANCE', name='plotstatus'), nullable=True))
    op.add_column('plots', sa.Column('elevation', sa.Float(), nullable=True))
    op.add_column('plots', sa.Column('slope', sa.Float(), nullable=True))
    op.add_column('plots', sa.Column('soil_type', sa.String(100), nullable=True))
    op.add_column('plots', sa.Column('ph_level', sa.Float(), nullable=True))
    op.add_column('plots', sa.Column('nitrogen_level', sa.Float(), nullable=True))
    op.add_column('plots', sa.Column('phosphorus_level', sa.Float(), nullable=True))
    op.add_column('plots', sa.Column('potassium_level', sa.Float(), nullable=True))
    op.add_column('plots', sa.Column('organic_matter', sa.Float(), nullable=True))
    op.add_column('plots', sa.Column('current_crop', sa.String(100), nullable=True))
    op.add_column('plots', sa.Column('crop_variety', sa.String(100), nullable=True))
    op.add_column('plots', sa.Column('planting_date', sa.DateTime(), nullable=True))
    op.add_column('plots', sa.Column('expected_harvest_date', sa.DateTime(), nullable=True))
    op.add_column('plots', sa.Column('last_harvest_date', sa.DateTime(), nullable=True))
    op.add_column('plots', sa.Column('livestock_type', sa.String(100), nullable=True))
    op.add_column('plots', sa.Column('livestock_count', sa.Integer(), nullable=True))
    op.add_column('plots', sa.Column('grazing_capacity', sa.Integer(), nullable=True))
    op.add_column('plots', sa.Column('irrigation_type', sa.String(50), nullable=True))
    op.add_column('plots', sa.Column('water_source', sa.String(100), nullable=True))