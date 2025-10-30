"""add versioning tables

Revision ID: 006_add_versioning
Revises: 005_add_is_system_role
Create Date: 2025-10-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Add version column to users table
    op.add_column('users', sa.Column('version', sa.Integer(), nullable=False, server_default='1'), schema='auth_db')

    # Add version column to roles table
    op.add_column('roles', sa.Column('version', sa.Integer(), nullable=False, server_default='1'), schema='auth_db')

    # Create user_history table
    op.create_table('user_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('changed_by', sa.Integer(), nullable=True),
        sa.Column('change_reason', sa.String(length=500), nullable=True),
        sa.Column('change_type', sa.String(length=50), nullable=False),

        # Snapshot fields
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=True),
        sa.Column('user_type', sa.String(length=20), nullable=False),
        sa.Column('ad_sync_id', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False),
        sa.Column('mfa_enabled', sa.Boolean(), nullable=False),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_ip', sa.String(length=45), nullable=True),
        sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('require_password_change', sa.Boolean(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.Column('original_created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('original_updated_at', sa.DateTime(timezone=True), nullable=False),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['auth_db.users.id'], ),
        schema='auth_db'
    )
    op.create_index('ix_auth_db_user_history_user_id', 'user_history', ['user_id'], unique=False, schema='auth_db')

    # Create role_history table
    op.create_table('role_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('changed_by', sa.Integer(), nullable=True),
        sa.Column('change_reason', sa.String(length=500), nullable=True),
        sa.Column('change_type', sa.String(length=50), nullable=False),

        # Snapshot fields
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('original_created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('original_updated_at', sa.DateTime(timezone=True), nullable=False),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['role_id'], ['auth_db.roles.id'], ),
        schema='auth_db'
    )
    op.create_index('ix_auth_db_role_history_role_id', 'role_history', ['role_id'], unique=False, schema='auth_db')


def downgrade():
    # Drop indexes
    op.drop_index('ix_auth_db_role_history_role_id', table_name='role_history', schema='auth_db')
    op.drop_index('ix_auth_db_user_history_user_id', table_name='user_history', schema='auth_db')

    # Drop tables
    op.drop_table('role_history', schema='auth_db')
    op.drop_table('user_history', schema='auth_db')

    # Drop version columns
    op.drop_column('roles', 'version', schema='auth_db')
    op.drop_column('users', 'version', schema='auth_db')
