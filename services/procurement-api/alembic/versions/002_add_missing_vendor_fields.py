"""add_missing_vendor_fields

Revision ID: 002
Revises: 001
Create Date: 2025-11-03 01:00:00

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing columns to vendors table"""
    # Add business_registration column
    op.add_column(
        "vendors",
        sa.Column("business_registration", sa.String(length=100), nullable=True),
        schema="procurement_db",
    )

    # Add bank_account column
    op.add_column(
        "vendors",
        sa.Column("bank_account", sa.String(length=100), nullable=True),
        schema="procurement_db",
    )

    # Add bank_name column
    op.add_column(
        "vendors",
        sa.Column("bank_name", sa.String(length=255), nullable=True),
        schema="procurement_db",
    )

    # Add created_by column
    op.add_column(
        "vendors",
        sa.Column("created_by", sa.Integer(), nullable=False, server_default="1"),
        schema="procurement_db",
    )

    # Add deleted_at column
    op.add_column(
        "vendors",
        sa.Column("deleted_at", sa.TIMESTAMP(), nullable=True),
        schema="procurement_db",
    )


def downgrade() -> None:
    """Remove added columns from vendors table"""
    op.drop_column("vendors", "deleted_at", schema="procurement_db")
    op.drop_column("vendors", "created_by", schema="procurement_db")
    op.drop_column("vendors", "bank_name", schema="procurement_db")
    op.drop_column("vendors", "bank_account", schema="procurement_db")
    op.drop_column("vendors", "business_registration", schema="procurement_db")
