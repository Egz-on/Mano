"""sync_user_profiles_and_constraints

Revision ID: d8c78c0bd271
Revises: ef2fbb99bced
Create Date: 2026-04-22 18:06:00.460933

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from mano.infrastructure.database.models import GUID


# revision identifiers, used by Alembic.
revision: str = 'd8c78c0bd271'
down_revision: Union[str, Sequence[str], None] = 'ef2fbb99bced'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns as nullable first (for data migration)
    op.add_column('user_profiles', sa.Column('name', sa.String(length=255), nullable=True))
    op.add_column('user_profiles', sa.Column('surname', sa.String(length=255), nullable=True))

    # Migrate data: split full_name into name and surname
    op.execute(
        "UPDATE user_profiles SET "
        "name = split_part(full_name, ' ', 1), "
        "surname = CASE WHEN position(' ' in full_name) > 0 "
        "  THEN substring(full_name from position(' ' in full_name) + 1) "
        "  ELSE '' END"
    )

    # Make name/surname NOT NULL after data migration
    op.alter_column('user_profiles', 'name', nullable=False)
    op.alter_column('user_profiles', 'surname', nullable=False)

    # Re-add columns that were previously dropped, with server defaults
    op.add_column('user_profiles', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')))
    op.add_column('user_profiles', sa.Column('is_online', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('user_profiles', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('user_profiles', sa.Column('longitude', sa.Float(), nullable=True))
    op.add_column('user_profiles', sa.Column('approval_status', sa.String(length=20), nullable=False, server_default='pending'))
    op.add_column('user_profiles', sa.Column('fcm_token', sa.String(length=500), nullable=True))

    # Drop old full_name column
    op.drop_column('user_profiles', 'full_name')


def downgrade() -> None:
    """Downgrade schema."""
    # Re-add full_name as nullable first
    op.add_column('user_profiles', sa.Column('full_name', sa.VARCHAR(length=255), nullable=True))

    # Reconstruct full_name from name and surname
    op.execute(
        "UPDATE user_profiles SET full_name = CONCAT(name, ' ', surname)"
    )

    # Make full_name NOT NULL
    op.alter_column('user_profiles', 'full_name', nullable=False)

    # Drop new columns
    op.drop_column('user_profiles', 'fcm_token')
    op.drop_column('user_profiles', 'approval_status')
    op.drop_column('user_profiles', 'longitude')
    op.drop_column('user_profiles', 'latitude')
    op.drop_column('user_profiles', 'is_online')
    op.drop_column('user_profiles', 'is_active')
    op.drop_column('user_profiles', 'surname')
    op.drop_column('user_profiles', 'name')
