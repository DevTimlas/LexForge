# File: lexforge-backend/migrations/env.py
import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, project_root)

from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from app.models.base import Base
from app.models.user import User
from app.models.document import Document
from app.models.alert import Alert
from app.models.user_metrics import UserMetrics
from app.models.feedback import Feedback

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

# Get the database URL from config
connectable = create_engine(
    config.get_main_option("sqlalchemy.url"),
    poolclass=pool.NullPool
)

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()