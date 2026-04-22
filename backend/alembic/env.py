"""Alembic environment configuration with async support."""

import asyncio
import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import our models metadata
from mano.infrastructure.config.settings import DatabaseSettings
from mano.infrastructure.database.models import Base

# this is the Alembic Config object
config = context.config

# Override hardcoded alembic.ini URL with environment-aware settings
db_settings = DatabaseSettings()
config.set_main_option("sqlalchemy.url", db_settings.url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

# Tables where unique constraints are defined via column-level unique=True
# in models but were also created as named UniqueConstraint in migrations.
# Alembic sees the DB constraint but not the metadata one, producing false-positive
# "remove constraint" operations during autogenerate.
_CONSTRAINT_DRIFT_TABLES = {"auth_credentials", "password_reset_tokens"}
_POSTGIS_EXTENSION_SCHEMAS = {"tiger", "tiger_data", "topology"}
_POSTGIS_EXTENSION_TABLES = {
    "addr",
    "addrfeat",
    "bg",
    "county",
    "county_lookup",
    "countysub_lookup",
    "cousub",
    "direction_lookup",
    "edges",
    "faces",
    "featnames",
    "geocode_settings",
    "geocode_settings_default",
    "geometry_columns",
    "geography_columns",
    "layer",
    "loader_lookuptables",
    "loader_platform",
    "loader_variables",
    "pagc_gaz",
    "pagc_lex",
    "pagc_rules",
    "place",
    "place_lookup",
    "raster_columns",
    "raster_overviews",
    "secondary_unit_lookup",
    "spatial_ref_sys",
    "state",
    "state_lookup",
    "street_type_lookup",
    "tabblock",
    "tabblock20",
    "topology",
    "tract",
    "zcta5",
    "zip_lookup",
    "zip_lookup_all",
    "zip_lookup_base",
    "zip_state",
    "zip_state_loc",
}


def _object_table_name(object, type_, name):
    """Return the associated table name for Alembic objects when available."""
    if type_ == "table":
        return name
    table = getattr(object, "table", None)
    return getattr(table, "name", None)


def _object_schema_name(object) -> str | None:
    """Return the schema name for Alembic objects when available."""
    schema = getattr(object, "schema", None)
    if schema is not None:
        return schema
    table = getattr(object, "table", None)
    return getattr(table, "schema", None)


def _render_item(type_, obj, autogen_context):
    """Add required imports for custom-rendered types."""
    module_name = getattr(obj.__class__, "__module__", "")
    if type_ == "type" and ("geoalchemy2" in module_name or "Geometry" in repr(obj)):
        autogen_context.imports.add("import geoalchemy2")
    return False


def _include_object(object, name, type_, reflected, compare_to):
    """Skip false-positive unique constraint removals on specific tables.

    When a unique constraint exists in the DB (reflected=True) but has no
    corresponding metadata object (compare_to=None), Alembic wants to drop it.
    For tables where unique=True on columns already covers the intent, this
    is a false positive.
    """
    table_name = _object_table_name(object, type_, name)
    schema_name = _object_schema_name(object)
    if reflected and compare_to is None:
        if schema_name in _POSTGIS_EXTENSION_SCHEMAS or table_name in _POSTGIS_EXTENSION_TABLES:
            return False
    if (
        type_ == "unique_constraint"
        and reflected
        and compare_to is None
    ):
        if table_name in _CONSTRAINT_DRIFT_TABLES:
            return False
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_object=_include_object,
        render_item=_render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        include_object=_include_object,
        render_item=_render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
