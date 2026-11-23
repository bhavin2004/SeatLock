"""add review required payment status

Revision ID: 36fe453adde6
Revises: 1972ef711895
Create Date: 2026-11-23 09:15:12.821999

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36fe453adde6'
down_revision: Union[str, Sequence[str], None] = '1972ef711895'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE payment_status_enum ADD VALUE 'review_required'")
    pass


def downgrade() -> None:
    """Downgrade schema."""
    raise NotImplementedError(
        "Removing review_required requires a separate migration."
    )
