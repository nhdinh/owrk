"""Add missing user fields

Revision ID: 002
Revises: 001
Create Date: 2025-10-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to users table
    op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'), schema='auth_db')
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'), schema='auth_db')
    op.add_column('users', sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True), schema='auth_db')
    op.add_column('users', sa.Column('require_password_change', sa.Boolean(), nullable=False, server_default='false'), schema='auth_db')
    op.add_column('users', sa.Column('department_id', sa.Integer(), nullable=True), schema='auth_db')
    op.add_column('users', sa.Column('address', sa.Text(), nullable=True), schema='auth_db')

    # Rename department column to avoid conflict (if needed by user's changes)
    # The original migration has 'department' but model may expect 'department_id'
    # We'll keep both for now - user can decide which to use


def downgrade() -> None:
    # Remove added columns
    op.drop_column('users', 'address', schema='auth_db')
    op.drop_column('users', 'department_id', schema='auth_db')
    op.drop_column('users', 'require_password_change', schema='auth_db')
    op.drop_column('users', 'password_changed_at', schema='auth_db')
    op.drop_column('users', 'email_verified', schema='auth_db')
    op.drop_column('users', 'is_superuser', schema='auth_db')
