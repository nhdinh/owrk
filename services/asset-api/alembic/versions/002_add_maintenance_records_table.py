"""add maintenance records table

Revision ID: 002
Revises: 32a6f5a3e6b6
Create Date: 2025-11-02 08:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "32a6f5a3e6b6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create maintenance_records table
    op.create_table(
        "maintenance_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("maintenance_type", sa.String(length=50), nullable=False),
        sa.Column("maintenance_date", sa.Date(), nullable=False),
        sa.Column("completed_date", sa.Date(), nullable=True),
        sa.Column(
            "cost",
            sa.Numeric(precision=15, scale=2),
            nullable=False,
            server_default="0",
        ),
        sa.Column("technician", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "status", sa.String(length=50), nullable=False, server_default="pending"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["asset_id"],
            ["asset_db.assets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="asset_db",
    )

    # Create indexes
    op.create_index(
        "ix_maintenance_records_asset_id",
        "maintenance_records",
        ["asset_id"],
        unique=False,
        schema="asset_db",
    )
    op.create_index(
        "ix_maintenance_records_maintenance_date",
        "maintenance_records",
        ["maintenance_date"],
        unique=False,
        schema="asset_db",
    )
    op.create_index(
        "ix_maintenance_records_status",
        "maintenance_records",
        ["status"],
        unique=False,
        schema="asset_db",
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index(
        "ix_maintenance_records_status",
        table_name="maintenance_records",
        schema="asset_db",
    )
    op.drop_index(
        "ix_maintenance_records_maintenance_date",
        table_name="maintenance_records",
        schema="asset_db",
    )
    op.drop_index(
        "ix_maintenance_records_asset_id",
        table_name="maintenance_records",
        schema="asset_db",
    )

    # Drop table
    op.drop_table("maintenance_records", schema="asset_db")
