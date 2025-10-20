"""add timestamps to refresh_tokens and other tables

Revision ID: 004
Revises: 003
Create Date: 2025-10-20

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Add updated_at to refresh_tokens (created_at already exists)
    op.add_column(
        'refresh_tokens',
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        schema='auth_db'
    )

    # Add updated_at to password_reset_tokens (created_at already exists)
    op.add_column(
        'password_reset_tokens',
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        schema='auth_db'
    )

    # Add updated_at to mfa_backup_codes (created_at already exists)
    op.add_column(
        'mfa_backup_codes',
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        schema='auth_db'
    )


def downgrade():
    # Remove updated_at from all tables (leave created_at)
    op.drop_column('mfa_backup_codes', 'updated_at', schema='auth_db')
    op.drop_column('password_reset_tokens', 'updated_at', schema='auth_db')
    op.drop_column('refresh_tokens', 'updated_at', schema='auth_db')
