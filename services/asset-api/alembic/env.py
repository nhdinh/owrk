from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import Base and all models
from app.core.database import Base
from app.core.config import settings
from app.models.asset import Asset
from app.models.category import AssetCategory
from app.models.assignment import AssetAssignment
from app.models.attachment import AssetAttachment
from app.models.depreciation import AssetDepreciationRecord

# this is the Alembic Config object
config = context.config

# Set sqlalchemy.url from settings
# Note: Don't use set_main_option with URLs containing % characters (URL encoding)
# Instead, we'll use the URL directly in run_migrations_online()

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # Use DATABASE_URL directly to avoid URL encoding issues
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Use the database engine directly to avoid URL encoding issues
    from app.core.database import engine

    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
