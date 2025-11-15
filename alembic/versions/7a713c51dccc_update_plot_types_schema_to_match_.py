"""Update plot types schema to match simplified model

Revision ID: 7a713c51dccc
Revises: 0ed609fe3f23
Create Date: 2025-10-07 21:13:30.410794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a713c51dccc'
down_revision: Union[str, Sequence[str], None] = '0ed609fe3f23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Update field_plot_types - remove crop_type, fertilizer_schedule, harvest_season
    op.drop_column('field_plot_types', 'crop_type')
    op.drop_column('field_plot_types', 'fertilizer_schedule')
    op.drop_column('field_plot_types', 'harvest_season')
    
    # Update barn_plot_types - remove all existing columns and add structure_type
    op.drop_column('barn_plot_types', 'capacity')
    op.drop_column('barn_plot_types', 'equipment_stored')
    op.drop_column('barn_plot_types', 'ventilation_system')
    op.drop_column('barn_plot_types', 'electricity_available')
    op.drop_column('barn_plot_types', 'water_access')
    op.add_column('barn_plot_types', sa.Column('structure_type', sa.String(length=100), nullable=True))
    
    # Update pasture_plot_types - remove all existing columns and add status
    op.drop_column('pasture_plot_types', 'grass_type')
    op.drop_column('pasture_plot_types', 'livestock_capacity')
    op.drop_column('pasture_plot_types', 'fencing_type')
    op.drop_column('pasture_plot_types', 'water_source')
    op.drop_column('pasture_plot_types', 'grazing_season')
    op.add_column('pasture_plot_types', sa.Column('status', sa.String(length=50), nullable=True))
    
    # Update greenhouse_plot_types - remove all existing columns and add greenhouse_type
    op.drop_column('greenhouse_plot_types', 'climate_control')
    op.drop_column('greenhouse_plot_types', 'heating_system')
    op.drop_column('greenhouse_plot_types', 'cooling_system')
    op.drop_column('greenhouse_plot_types', 'humidity_control')
    op.drop_column('greenhouse_plot_types', 'growing_medium')
    op.add_column('greenhouse_plot_types', sa.Column('greenhouse_type', sa.String(length=100), nullable=True))
    
    # Update natural_area_plot_types - keep ecosystem_type, remove others, add default
    op.drop_column('natural_area_plot_types', 'conservation_status')
    op.drop_column('natural_area_plot_types', 'wildlife_present')
    op.drop_column('natural_area_plot_types', 'management_plan')
    op.drop_column('natural_area_plot_types', 'access_restrictions')
    op.alter_column('natural_area_plot_types', 'ecosystem_type', server_default=sa.text("'Wild'"))
    
    # Update water_source_plot_types - keep source_type and depth, remove others
    op.drop_column('water_source_plot_types', 'water_quality')
    op.drop_column('water_source_plot_types', 'flow_rate')
    op.drop_column('water_source_plot_types', 'treatment_required')


def downgrade() -> None:
    """Downgrade schema."""
    # Restore water_source_plot_types columns
    op.add_column('water_source_plot_types', sa.Column('treatment_required', sa.String(length=20), nullable=True))
    op.add_column('water_source_plot_types', sa.Column('flow_rate', sa.String(length=50), nullable=True))
    op.add_column('water_source_plot_types', sa.Column('water_quality', sa.String(length=100), nullable=True))
    
    # Restore natural_area_plot_types columns
    op.alter_column('natural_area_plot_types', 'ecosystem_type', server_default=None)
    op.add_column('natural_area_plot_types', sa.Column('access_restrictions', sa.Text(), nullable=True))
    op.add_column('natural_area_plot_types', sa.Column('management_plan', sa.Text(), nullable=True))
    op.add_column('natural_area_plot_types', sa.Column('wildlife_present', sa.Text(), nullable=True))
    op.add_column('natural_area_plot_types', sa.Column('conservation_status', sa.String(length=100), nullable=True))
    
    # Restore greenhouse_plot_types columns
    op.drop_column('greenhouse_plot_types', 'greenhouse_type')
    op.add_column('greenhouse_plot_types', sa.Column('growing_medium', sa.String(length=100), nullable=True))
    op.add_column('greenhouse_plot_types', sa.Column('humidity_control', sa.String(length=100), nullable=True))
    op.add_column('greenhouse_plot_types', sa.Column('cooling_system', sa.String(length=100), nullable=True))
    op.add_column('greenhouse_plot_types', sa.Column('heating_system', sa.String(length=100), nullable=True))
    op.add_column('greenhouse_plot_types', sa.Column('climate_control', sa.String(length=100), nullable=True))
    
    # Restore pasture_plot_types columns
    op.drop_column('pasture_plot_types', 'status')
    op.add_column('pasture_plot_types', sa.Column('grazing_season', sa.String(length=50), nullable=True))
    op.add_column('pasture_plot_types', sa.Column('water_source', sa.String(length=100), nullable=True))
    op.add_column('pasture_plot_types', sa.Column('fencing_type', sa.String(length=100), nullable=True))
    op.add_column('pasture_plot_types', sa.Column('livestock_capacity', sa.Integer(), nullable=True))
    op.add_column('pasture_plot_types', sa.Column('grass_type', sa.String(length=100), nullable=True))
    
    # Restore barn_plot_types columns
    op.drop_column('barn_plot_types', 'structure_type')
    op.add_column('barn_plot_types', sa.Column('water_access', sa.String(length=20), nullable=True))
    op.add_column('barn_plot_types', sa.Column('electricity_available', sa.String(length=20), nullable=True))
    op.add_column('barn_plot_types', sa.Column('ventilation_system', sa.String(length=100), nullable=True))
    op.add_column('barn_plot_types', sa.Column('equipment_stored', sa.Text(), nullable=True))
    op.add_column('barn_plot_types', sa.Column('capacity', sa.Integer(), nullable=True))
    
    # Restore field_plot_types columns
    op.add_column('field_plot_types', sa.Column('harvest_season', sa.String(length=50), nullable=True))
    op.add_column('field_plot_types', sa.Column('fertilizer_schedule', sa.Text(), nullable=True))
    op.add_column('field_plot_types', sa.Column('crop_type', sa.String(length=100), nullable=True))
