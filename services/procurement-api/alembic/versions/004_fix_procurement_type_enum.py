"""fix_procurement_type_enum

Revision ID: 004
Revises: 003
Create Date: 2025-11-03 01:48:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Update procurement_type enum to match model"""

    # For MySQL, we need to modify the enum by changing the column type
    op.execute("""
        ALTER TABLE procurement_db.purchase_requests
        MODIFY COLUMN procurement_type
        ENUM('FRAMEWORK_CONTRACT', 'ONE_TIME') NOT NULL
    """)


def downgrade() -> None:
    """Revert procurement_type enum to original values"""

    op.execute("""
        ALTER TABLE procurement_db.purchase_requests
        MODIFY COLUMN procurement_type
        ENUM('GOODS', 'SERVICES', 'BOTH') NOT NULL
    """)
