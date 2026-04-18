from __future__ import annotations

from sqlalchemy import inspect

from alembic import command
from alembic.config import Config
from app.core.config import get_settings
from app.db.session import engine


def _alembic_config() -> Config:
    settings = get_settings()
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", settings.database_url)
    return config


def upgrade_database() -> None:
    config = _alembic_config()
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    # This keeps local developer databases usable after earlier create_all-based runs.
    if existing_tables and "alembic_version" not in existing_tables:
        command.stamp(config, "head")

    command.upgrade(config, "head")


if __name__ == "__main__":
    upgrade_database()
