"""Updated plot table - removed extra columns

Revision ID: 0e701b860cf4
Revises: b159ff1544cc
Create Date: 2025-10-06 20:22:44.363897

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0e701b860cf4'
down_revision: Union[str, Sequence[str], None] = 'b159ff1544cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Update PlotType enum to use new values
    op.execute("ALTER TYPE plottype RENAME TO plottype_old")
    op.execute("CREATE TYPE plottype AS ENUM ('FIELD', 'BARN', 'PASTURE', 'GREEN_HOUSE', 'CHICKEN_PEN', 'COW_SHED', 'FISH_POND', 'RESIDENCE', 'NATURAL_AREA', 'WATER_SOURCE')")
    op.execute("ALTER TABLE plots ALTER COLUMN plot_type TYPE plottype USING plot_type::text::plottype")
    op.execute("DROP TYPE plottype_old")


def downgrade() -> None:
    """Downgrade schema."""
    # Revert PlotType enum to old values
    op.execute("ALTER TYPE plottype RENAME TO plottype_new")
    op.execute("CREATE TYPE plottype AS ENUM ('CROP', 'LIVESTOCK', 'MIXED', 'FORESTRY', 'AQUACULTURE', 'GREENHOUSE', 'ORCHARD', 'PASTURE')")
    op.execute("ALTER TABLE plots ALTER COLUMN plot_type TYPE plottype USING plot_type::text::plottype")
    op.execute("DROP TYPE plottype_new")