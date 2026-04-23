"""user-location

Revision ID: 78498962f145
Revises: 7e9f5bb8c2a1
Create Date: 2026-04-22 21:50:47.511496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = '78498962f145'
down_revision: Union[str, Sequence[str], None] = '7e9f5bb8c2a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "user_profiles",
        sa.Column(
            "location",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                dimension=2,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ).with_variant(sa.Text(), "sqlite"),
            nullable=True,
        ),
    )
    op.execute(
        """
        UPDATE user_profiles
        SET location = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
        """
    )
    # GeoAlchemy2 creates the GiST spatial index for Geometry columns using the
    # conventional "idx_<table>_<column>" name, so creating it manually here
    # collides with the auto-generated relation during the same migration.
    op.drop_column("user_profiles", "latitude")
    op.drop_column("user_profiles", "longitude")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "user_profiles",
        sa.Column("longitude", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column("latitude", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    )
    op.execute(
        """
        UPDATE user_profiles
        SET
            longitude = ST_X(location),
            latitude = ST_Y(location)
        WHERE location IS NOT NULL
        """
    )
    op.drop_column("user_profiles", "location")
