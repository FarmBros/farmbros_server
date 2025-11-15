"""Add login_type column to users table

Revision ID: e235af1636a8
Revises: 27a7f546286e
Create Date: 2025-08-26 22:18:44.190222

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e235af1636a8'
down_revision: Union[str, Sequence[str], None] = '27a7f546286e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum type for login_type
    login_type_enum = sa.Enum('PASSWORD', 'GOOGLE_AUTH', 'BOTH', name='logintype')
    login_type_enum.create(op.get_bind())
    
    # Add login_type column to users table
    op.add_column('users', sa.Column('login_type', login_type_enum, nullable=False, server_default='PASSWORD'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove login_type column
    op.drop_column('users', 'login_type')
    
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS logintype")