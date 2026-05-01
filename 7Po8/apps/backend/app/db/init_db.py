from pathlib import Path

from alembic.config import Config
from sqlalchemy import inspect

from alembic import command
from app.db.session import DatabaseManager


def _build_alembic_config(database_url: str) -> Config:
    backend_dir = Path(__file__).resolve().parents[2]
    alembic_ini_path = backend_dir / "alembic.ini"
    config = Config(str(alembic_ini_path))
    config.set_main_option("script_location", str(backend_dir / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def init_db(db: DatabaseManager) -> None:
    config = _build_alembic_config(db._url)  # noqa: SLF001
    inspector = inspect(db.engine)
    table_names = set(inspector.get_table_names())
    has_alembic_version = "alembic_version" in table_names
    has_existing_schema = bool(table_names - {"alembic_version"})
    if has_existing_schema and not has_alembic_version:
        command.stamp(config, "head")
    command.upgrade(config, "head")
