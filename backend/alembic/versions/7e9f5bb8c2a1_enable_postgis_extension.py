"""enable postgis extension

Revision ID: 7e9f5bb8c2a1
Revises: d8c78c0bd271
Create Date: 2026-04-22 20:25:00.000000

"""

from typing import Union
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7e9f5bb8c2a1"
down_revision: str | Sequence[str] | None = "d8c78c0bd271"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Enable PostGIS for the application database."""
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")


def downgrade() -> None:
    """Remove PostGIS if this migration is rolled back."""
    op.execute("DROP EXTENSION IF EXISTS postgis")
