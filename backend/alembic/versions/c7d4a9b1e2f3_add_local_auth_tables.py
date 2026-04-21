"""add local auth tables

Revision ID: c7d4a9b1e2f3
Revises: 36bfd954b68a
Create Date: 2026-02-12 16:00:00.000000

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from mano.infrastructure.database.models import GUID


# revision identifiers, used by Alembic.
revision: str = "c7d4a9b1e2f3"
down_revision: str | Sequence[str] | None = "36bfd954b68a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_profile_columns = {column["name"] for column in inspector.get_columns("user_profiles")}

    if "auth_user_id" not in user_profile_columns:
        op.add_column("user_profiles", sa.Column("auth_user_id", GUID(), nullable=True))
        op.execute("UPDATE user_profiles SET auth_user_id = id WHERE auth_user_id IS NULL")

        op.alter_column("user_profiles", "auth_user_id", nullable=False)

    user_profile_indexes = {index["name"] for index in inspector.get_indexes("user_profiles")}
    auth_user_id_index_name = op.f("ix_user_profiles_auth_user_id")
    if auth_user_id_index_name not in user_profile_indexes:
        op.create_index(auth_user_id_index_name, "user_profiles", ["auth_user_id"], unique=True)

    op.create_table(
        "auth_credentials",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("auth_user_id", GUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["auth_user_id"], ["user_profiles.auth_user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("auth_user_id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_auth_credentials_auth_user_id"), "auth_credentials", ["auth_user_id"], unique=True)
    op.create_index(op.f("ix_auth_credentials_email"), "auth_credentials", ["email"], unique=True)

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("auth_user_id", GUID(), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["auth_user_id"], ["auth_credentials.auth_user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(op.f("ix_password_reset_tokens_auth_user_id"), "password_reset_tokens", ["auth_user_id"], unique=False)
    op.create_index(op.f("ix_password_reset_tokens_expires_at"), "password_reset_tokens", ["expires_at"], unique=False)
    op.create_index(op.f("ix_password_reset_tokens_token_hash"), "password_reset_tokens", ["token_hash"], unique=True)
    op.create_index(op.f("ix_password_reset_tokens_used_at"), "password_reset_tokens", ["used_at"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_password_reset_tokens_used_at"), table_name="password_reset_tokens")
    op.drop_index(op.f("ix_password_reset_tokens_token_hash"), table_name="password_reset_tokens")
    op.drop_index(op.f("ix_password_reset_tokens_expires_at"), table_name="password_reset_tokens")
    op.drop_index(op.f("ix_password_reset_tokens_auth_user_id"), table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")

    op.drop_index(op.f("ix_auth_credentials_email"), table_name="auth_credentials")
    op.drop_index(op.f("ix_auth_credentials_auth_user_id"), table_name="auth_credentials")
    op.drop_table("auth_credentials")
