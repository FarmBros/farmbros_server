"""Add google_id column to users table

Revision ID: 27a7f546286e
Revises: d8e4ec6bbe7f
Create Date: 2025-08-26 19:40:54.927558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '27a7f546286e'
down_revision: Union[str, Sequence[str], None] = 'd8e4ec6bbe7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add google_id column to users table
    op.add_column('users', sa.Column('google_id', sa.String(length=255), nullable=True))
    
    # Make password_hash nullable to support Google OAuth users
    op.alter_column('users', 'password_hash',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    
    # Create unique index on google_id
    op.create_index(op.f('ix_users_google_id'), 'users', ['google_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the index
    op.drop_index(op.f('ix_users_google_id'), table_name='users')
    
    # Make password_hash non-nullable again
    op.alter_column('users', 'password_hash',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    
    # Remove google_id column
    op.drop_column('users', 'google_id')