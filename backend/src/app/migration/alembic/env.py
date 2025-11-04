import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add parent directories to path to import models
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

# Import models to register them with SQLModel
from src.app.repository.orm import SQLModelWithSort, UserORM

# Import all other models here as you add them
# from src.app.repository.other_models import OtherORM

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get metadata from SQLModel
target_metadata = SQLModelWithSort.metadata

# Override database URL from secrets if not in alembic.ini
from src.app.utils.secrets import get_sync_db_url
if config.get_main_option("sqlalchemy.url") == "driver://user:pass@localhost/dbname":
    # Use actual database URL from secrets
    db_url = get_sync_db_url("primary")
    config.set_main_option("sqlalchemy.url", db_url)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    if url == "driver://user:pass@localhost/dbname":
        url = get_sync_db_url("primary")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get database URL from config or secrets
    url = config.get_main_option("sqlalchemy.url")
    if url == "driver://user:pass@localhost/dbname":
        url = get_sync_db_url("primary")
    
    connectable = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
