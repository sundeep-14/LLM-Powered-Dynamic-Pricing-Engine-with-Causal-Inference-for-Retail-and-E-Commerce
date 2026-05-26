"""
env.py
------
Alembic reads this file to know:
1. How to connect to the database
2. Which models to watch for changes

You should not need to change this file unless
you change your database URL setup.
"""

import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# This adds your project root to Python's path
# So imports like "from database.session import Base" work correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Load .env file so DATABASE_URL is available
load_dotenv()

# Alembic Config object — reads alembic.ini
config = context.config

# Override the sqlalchemy.url with value from .env
# This way your DB credentials are never hardcoded here
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base and ALL models so Alembic can detect table changes
# This is why __init__.py imports all models — one import covers all
from database.session import Base
import database.models  # noqa: F401

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations without a live DB connection.
    Generates a SQL script file instead.
    Useful when you want to review SQL before running it.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations against a live DB connection.
    This is what runs when you do: alembic upgrade head
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


# Alembic decides which function to call based on the command used
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()