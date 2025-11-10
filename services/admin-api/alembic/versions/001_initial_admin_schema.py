"""initial_admin_schema

Revision ID: 001
Revises:
Create Date: 2025-11-08 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create schema if it doesn't exist
    op.execute("CREATE SCHEMA IF NOT EXISTS admin_db")

    # Create module_settings table
    op.create_table(
        "module_settings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("module_name", sa.String(length=50), nullable=False),
        sa.Column("setting_key", sa.String(length=100), nullable=False),
        sa.Column("setting_value", sa.Text(), nullable=True),
        sa.Column("setting_type", sa.Enum("STRING", "INTEGER", "BOOLEAN", "JSON", name="settingtype"), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("is_public", sa.Boolean(), default=False),
        sa.Column("is_editable", sa.Boolean(), default=True),
        sa.Column("default_value", sa.Text(), nullable=True),
        sa.Column("validation_rules", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="admin_db",
    )
    op.create_index("ix_module_settings_id", "module_settings", ["id"], unique=False, schema="admin_db")
    op.create_index("ix_module_settings_module_name", "module_settings", ["module_name"], unique=False, schema="admin_db")
    op.create_index("ix_module_settings_setting_key", "module_settings", ["setting_key"], unique=False, schema="admin_db")

    # Create system_modules table
    op.create_table(
        "system_modules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("module_name", sa.String(length=50), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("version", sa.String(length=20), nullable=True),
        sa.Column("status", sa.Enum("ACTIVE", "INACTIVE", "MAINTENANCE", name="modulestatus"), nullable=False),
        sa.Column("api_endpoint", sa.String(length=500), nullable=True),
        sa.Column("frontend_endpoint", sa.String(length=500), nullable=True),
        sa.Column("icon", sa.String(length=50), nullable=True),
        sa.Column("sort_order", sa.Integer(), default=0),
        sa.Column("requires_auth", sa.Boolean(), default=True),
        sa.Column("allowed_roles", sa.Text(), nullable=True),
        sa.Column("is_system_module", sa.Boolean(), default=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        schema="admin_db",
    )
    op.create_index("ix_system_modules_id", "system_modules", ["id"], unique=False, schema="admin_db")
    op.create_index("ix_system_modules_module_name", "system_modules", ["module_name"], unique=True, schema="admin_db")

    # Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("user_email", sa.String(length=255), nullable=True),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("module_name", sa.String(length=50), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("changes", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        schema="admin_db",
    )
    op.create_index("ix_audit_logs_id", "audit_logs", ["id"], unique=False, schema="admin_db")
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"], unique=False, schema="admin_db")
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"], unique=False, schema="admin_db")
    op.create_index("ix_audit_logs_module_name", "audit_logs", ["module_name"], unique=False, schema="admin_db")
    op.create_index("ix_audit_logs_resource_type", "audit_logs", ["resource_type"], unique=False, schema="admin_db")
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"], unique=False, schema="admin_db")

    # Create system_logs table
    op.create_table(
        "system_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("log_level", sa.String(length=20), nullable=False),
        sa.Column("module_name", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("stack_trace", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        schema="admin_db",
    )
    op.create_index("ix_system_logs_id", "system_logs", ["id"], unique=False, schema="admin_db")
    op.create_index("ix_system_logs_log_level", "system_logs", ["log_level"], unique=False, schema="admin_db")
    op.create_index("ix_system_logs_module_name", "system_logs", ["module_name"], unique=False, schema="admin_db")
    op.create_index("ix_system_logs_created_at", "system_logs", ["created_at"], unique=False, schema="admin_db")

    # Insert default system modules
    op.execute("""
        INSERT INTO admin_db.system_modules
        (module_name, display_name, description, version, status, api_endpoint, frontend_endpoint, icon, sort_order, requires_auth, is_system_module)
        VALUES
        ('auth', 'Authentication', 'User authentication and authorization', '1.0.0', 'ACTIVE', 'http://auth-api:8000', 'http://localhost:8000/auth/', 'Shield', 1, TRUE, TRUE),
        ('asset', 'Asset Management', 'Manage office equipment assets', '1.0.0', 'ACTIVE', 'http://asset-api:8000', 'http://localhost:8000/assets/', 'Package', 2, TRUE, FALSE),
        ('procurement', 'Procurement', 'Procurement and purchasing management', '1.0.0', 'ACTIVE', 'http://procurement-api:8004', 'http://localhost:8000/procurement/', 'ShoppingCart', 3, TRUE, FALSE),
        ('dashboard', 'Dashboard', 'System dashboard and overview', '1.0.0', 'ACTIVE', 'http://dashboard-api:8000', 'http://localhost:8000/dashboard/', 'LayoutDashboard', 0, TRUE, TRUE),
        ('admin', 'Administration', 'System administration and settings', '1.0.0', 'ACTIVE', 'http://admin-api:8000', 'http://localhost:8000/admin/', 'Settings', 99, TRUE, TRUE)
    """)


def downgrade():
    op.drop_index("ix_system_logs_created_at", table_name="system_logs", schema="admin_db")
    op.drop_index("ix_system_logs_module_name", table_name="system_logs", schema="admin_db")
    op.drop_index("ix_system_logs_log_level", table_name="system_logs", schema="admin_db")
    op.drop_index("ix_system_logs_id", table_name="system_logs", schema="admin_db")
    op.drop_table("system_logs", schema="admin_db")

    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs", schema="admin_db")
    op.drop_index("ix_audit_logs_resource_type", table_name="audit_logs", schema="admin_db")
    op.drop_index("ix_audit_logs_module_name", table_name="audit_logs", schema="admin_db")
    op.drop_index("ix_audit_logs_action", table_name="audit_logs", schema="admin_db")
    op.drop_index("ix_audit_logs_user_id", table_name="audit_logs", schema="admin_db")
    op.drop_index("ix_audit_logs_id", table_name="audit_logs", schema="admin_db")
    op.drop_table("audit_logs", schema="admin_db")

    op.drop_index("ix_system_modules_module_name", table_name="system_modules", schema="admin_db")
    op.drop_index("ix_system_modules_id", table_name="system_modules", schema="admin_db")
    op.drop_table("system_modules", schema="admin_db")

    op.drop_index("ix_module_settings_setting_key", table_name="module_settings", schema="admin_db")
    op.drop_index("ix_module_settings_module_name", table_name="module_settings", schema="admin_db")
    op.drop_index("ix_module_settings_id", table_name="module_settings", schema="admin_db")
    op.drop_table("module_settings", schema="admin_db")

    op.execute("DROP SCHEMA IF EXISTS admin_db")
