"""add guest name/email fields to reviews

Revision ID: b7e2a1b9c4d5
Revises: 29bd92ab13c3
Create Date: 2026-04-17 12:20:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7e2a1b9c4d5"
down_revision: str | Sequence[str] | None = "29bd92ab13c3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("reviews", sa.Column("guest_name", sa.String(length=255), nullable=True))
    op.add_column("reviews", sa.Column("guest_email", sa.String(length=255), nullable=True))
    op.create_index(op.f("ix_reviews_guest_email"), "reviews", ["guest_email"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_reviews_guest_email"), table_name="reviews")
    op.drop_column("reviews", "guest_email")
    op.drop_column("reviews", "guest_name")
