"""Initial schema - Auth Service

Revision ID: 001
Revises:
Create Date: 2025-10-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create auth_db schema if not exists
    op.execute("CREATE SCHEMA IF NOT EXISTS auth_db")

    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        schema='auth_db'
    )
    op.create_index(op.f('ix_auth_db_roles_name'), 'roles', ['name'], unique=True, schema='auth_db')

    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('resource', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        schema='auth_db'
    )
    op.create_index(op.f('ix_auth_db_permissions_name'), 'permissions', ['name'], unique=True, schema='auth_db')
    op.create_index(op.f('ix_auth_db_permissions_resource'), 'permissions', ['resource'], schema='auth_db')

    # Create role_permissions junction table
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['auth_db.permissions.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['auth_db.roles.id'], ),
        sa.PrimaryKeyConstraint('role_id', 'permission_id'),
        schema='auth_db'
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=True),
        sa.Column('user_type', sa.String(length=20), nullable=False, server_default='local'),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.Column('mfa_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('mfa_secret', sa.String(length=255), nullable=True),
        sa.Column('backup_codes', sa.Text(), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_ip', sa.String(length=45), nullable=True),
        sa.Column('last_failed_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ad_sync_id', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['auth_db.roles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        schema='auth_db'
    )
    op.create_index(op.f('ix_auth_db_users_email'), 'users', ['email'], unique=True, schema='auth_db')
    op.create_index(op.f('ix_auth_db_users_username'), 'users', ['username'], unique=True, schema='auth_db')
    op.create_index(op.f('ix_auth_db_users_ad_sync_id'), 'users', ['ad_sync_id'], schema='auth_db')

    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=500), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['auth_db.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token'),
        schema='auth_db'
    )
    op.create_index(op.f('ix_auth_db_refresh_tokens_token'), 'refresh_tokens', ['token'], unique=True, schema='auth_db')
    op.create_index(op.f('ix_auth_db_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], schema='auth_db')

    # Create password_reset_tokens table
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['auth_db.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token'),
        schema='auth_db'
    )
    op.create_index(op.f('ix_auth_db_password_reset_tokens_token'), 'password_reset_tokens', ['token'], unique=True, schema='auth_db')
    op.create_index(op.f('ix_auth_db_password_reset_tokens_user_id'), 'password_reset_tokens', ['user_id'], schema='auth_db')

    # Create mfa_backup_codes table
    op.create_table(
        'mfa_backup_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('code_hash', sa.String(length=255), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['auth_db.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='auth_db'
    )
    op.create_index(op.f('ix_auth_db_mfa_backup_codes_user_id'), 'mfa_backup_codes', ['user_id'], schema='auth_db')

    # Insert default roles
    op.execute("""
        INSERT INTO auth_db.roles (name, display_name, description, is_active) VALUES
        ('admin', 'Administrator', 'Full system access', true),
        ('manager', 'Manager', 'Management level access', true),
        ('staff', 'Staff', 'Standard staff access', true),
        ('viewer', 'Viewer', 'Read-only access', true)
    """)

    # Insert default permissions
    op.execute("""
        INSERT INTO auth_db.permissions (name, resource, action, description) VALUES
        -- User permissions
        ('user:read', 'user', 'read', 'Read user information'),
        ('user:create', 'user', 'create', 'Create new users'),
        ('user:update', 'user', 'update', 'Update user information'),
        ('user:delete', 'user', 'delete', 'Delete users'),

        -- Role permissions
        ('role:read', 'role', 'read', 'Read role information'),
        ('role:create', 'role', 'create', 'Create new roles'),
        ('role:update', 'role', 'update', 'Update role information'),
        ('role:delete', 'role', 'delete', 'Delete roles'),

        -- Asset permissions
        ('asset:read', 'asset', 'read', 'Read asset information'),
        ('asset:create', 'asset', 'create', 'Create new assets'),
        ('asset:update', 'asset', 'update', 'Update asset information'),
        ('asset:delete', 'asset', 'delete', 'Delete assets'),

        -- Procurement permissions
        ('procurement:read', 'procurement', 'read', 'Read procurement information'),
        ('procurement:create', 'procurement', 'create', 'Create procurement requests'),
        ('procurement:update', 'procurement', 'update', 'Update procurement information'),
        ('procurement:approve', 'procurement', 'approve', 'Approve procurement requests'),

        -- Maintenance permissions
        ('maintenance:read', 'maintenance', 'read', 'Read maintenance information'),
        ('maintenance:create', 'maintenance', 'create', 'Create maintenance requests'),
        ('maintenance:update', 'maintenance', 'update', 'Update maintenance information'),
        ('maintenance:approve', 'maintenance', 'approve', 'Approve maintenance requests'),

        -- Report permissions
        ('report:read', 'report', 'read', 'Read reports'),
        ('report:create', 'report', 'create', 'Create reports'),
        ('report:export', 'report', 'export', 'Export reports')
    """)

    # Assign permissions to admin role (all permissions)
    op.execute("""
        INSERT INTO auth_db.role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM auth_db.roles r
        CROSS JOIN auth_db.permissions p
        WHERE r.name = 'admin'
    """)

    # Assign permissions to manager role (read, create, update for all resources)
    op.execute("""
        INSERT INTO auth_db.role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM auth_db.roles r
        CROSS JOIN auth_db.permissions p
        WHERE r.name = 'manager'
        AND p.action IN ('read', 'create', 'update', 'approve')
    """)

    # Assign permissions to staff role (read, create for most resources)
    op.execute("""
        INSERT INTO auth_db.role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM auth_db.roles r
        CROSS JOIN auth_db.permissions p
        WHERE r.name = 'staff'
        AND p.action IN ('read', 'create')
        AND p.resource != 'user'
    """)

    # Assign permissions to viewer role (read only)
    op.execute("""
        INSERT INTO auth_db.role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM auth_db.roles r
        CROSS JOIN auth_db.permissions p
        WHERE r.name = 'viewer'
        AND p.action = 'read'
    """)

    # Create default admin user (password: admin123)
    # Hash generated with: bcrypt.hashpw(b'admin123', bcrypt.gensalt())
    op.execute("""
        INSERT INTO auth_db.users (email, username, full_name, hashed_password, user_type, role_id, is_active)
        SELECT
            'admin@example.com',
            'admin',
            'System Administrator',
            '$2b$12$yk12wFneOEVCas/sZcLqXeXY8/uInVMwnHtjWW2QoL0CLlFdJl0ri',
            'local',
            r.id,
            true
        FROM auth_db.roles r
        WHERE r.name = 'admin'
    """)


def downgrade() -> None:
    # Drop all tables
    op.drop_table('mfa_backup_codes', schema='auth_db')
    op.drop_table('password_reset_tokens', schema='auth_db')
    op.drop_table('refresh_tokens', schema='auth_db')
    op.drop_table('users', schema='auth_db')
    op.drop_table('role_permissions', schema='auth_db')
    op.drop_table('permissions', schema='auth_db')
    op.drop_table('roles', schema='auth_db')

    # Drop schema
    op.execute("DROP SCHEMA IF EXISTS auth_db CASCADE")
