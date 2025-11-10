"""add_trash_tables

Revision ID: 002
Revises: 001
Create Date: 2025-11-08 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create trash_items table
    op.create_table(
        "trash_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("module_name", sa.String(length=50), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(length=100), nullable=False),
        sa.Column("resource_name", sa.String(length=500), nullable=False),
        sa.Column("resource_data", sa.JSON(), nullable=False),
        sa.Column("deleted_by", sa.Integer(), nullable=False),
        sa.Column("deleted_by_email", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_reason", sa.Text(), nullable=True),
        sa.Column("is_restorable", sa.Boolean(), default=True, nullable=False),
        sa.Column("permanent_delete_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("restore_dependencies", sa.JSON(), nullable=True),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
        sa.Column("restored_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("restored_by", sa.Integer(), nullable=True),
        sa.Column("restored_by_email", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="admin_db",
    )
    op.create_index("ix_trash_items_id", "trash_items", ["id"], unique=False, schema="admin_db")
    op.create_index("ix_trash_items_module_name", "trash_items", ["module_name"], unique=False, schema="admin_db")
    op.create_index("ix_trash_items_resource_type", "trash_items", ["resource_type"], unique=False, schema="admin_db")
    op.create_index("ix_trash_items_resource_id", "trash_items", ["resource_id"], unique=False, schema="admin_db")
    op.create_index("ix_trash_items_deleted_by", "trash_items", ["deleted_by"], unique=False, schema="admin_db")
    op.create_index("ix_trash_items_deleted_at", "trash_items", ["deleted_at"], unique=False, schema="admin_db")
    op.create_index("ix_trash_items_permanent_delete_at", "trash_items", ["permanent_delete_at"], unique=False, schema="admin_db")

    # Create trash_config table
    op.create_table(
        "trash_config",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("module_name", sa.String(length=50), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("auto_delete_days", sa.Integer(), default=30, nullable=False),
        sa.Column("enable_soft_delete", sa.Boolean(), default=True, nullable=False),
        sa.Column("enable_restore", sa.Boolean(), default=True, nullable=False),
        sa.Column("require_approval", sa.Boolean(), default=False, nullable=False),
        sa.Column("cascade_delete", sa.Boolean(), default=False, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        schema="admin_db",
    )
    op.create_index("ix_trash_config_id", "trash_config", ["id"], unique=False, schema="admin_db")
    op.create_index("ix_trash_config_module_name", "trash_config", ["module_name"], unique=False, schema="admin_db")
    op.create_index("ix_trash_config_resource_type", "trash_config", ["resource_type"], unique=False, schema="admin_db")
    op.create_index(
        "ix_trash_config_module_resource",
        "trash_config",
        ["module_name", "resource_type"],
        unique=True,
        schema="admin_db",
    )

    # Insert default trash configurations for existing modules
    op.execute("""
        INSERT INTO admin_db.trash_config
        (module_name, resource_type, auto_delete_days, enable_soft_delete, enable_restore, require_approval, cascade_delete)
        VALUES
        ('auth', 'user', 90, TRUE, TRUE, FALSE, FALSE),
        ('auth', 'role', 90, TRUE, TRUE, TRUE, FALSE),
        ('asset', 'asset', 365, TRUE, TRUE, FALSE, TRUE),
        ('asset', 'category', 90, TRUE, TRUE, TRUE, FALSE),
        ('procurement', 'purchase_request', 180, TRUE, TRUE, FALSE, FALSE),
        ('procurement', 'purchase_order', 365, TRUE, TRUE, FALSE, FALSE),
        ('procurement', 'vendor', 180, TRUE, TRUE, FALSE, FALSE),
        ('procurement', 'framework_contract', 730, TRUE, TRUE, TRUE, FALSE)
    """)


def downgrade():
    op.drop_index("ix_trash_config_module_resource", table_name="trash_config", schema="admin_db")
    op.drop_index("ix_trash_config_resource_type", table_name="trash_config", schema="admin_db")
    op.drop_index("ix_trash_config_module_name", table_name="trash_config", schema="admin_db")
    op.drop_index("ix_trash_config_id", table_name="trash_config", schema="admin_db")
    op.drop_table("trash_config", schema="admin_db")

    op.drop_index("ix_trash_items_permanent_delete_at", table_name="trash_items", schema="admin_db")
    op.drop_index("ix_trash_items_deleted_at", table_name="trash_items", schema="admin_db")
    op.drop_index("ix_trash_items_deleted_by", table_name="trash_items", schema="admin_db")
    op.drop_index("ix_trash_items_resource_id", table_name="trash_items", schema="admin_db")
    op.drop_index("ix_trash_items_resource_type", table_name="trash_items", schema="admin_db")
    op.drop_index("ix_trash_items_module_name", table_name="trash_items", schema="admin_db")
    op.drop_index("ix_trash_items_id", table_name="trash_items", schema="admin_db")
    op.drop_table("trash_items", schema="admin_db")
