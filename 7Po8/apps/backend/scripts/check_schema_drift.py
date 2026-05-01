from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine
from sqlmodel import SQLModel

from alembic import command
from app.models import (  # noqa: F401
    Connector,
    DiscoveredSource,
    DomainTrustProfile,
    PolicyActionLog,
    Record,
    RunHistory,
    Signal,
    SourceCheck,
    Wave,
    WaveDomainTrustOverride,
)


def build_alembic_config(database_url: str) -> Config:
    backend_dir = Path(__file__).resolve().parents[1]
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("script_location", str(backend_dir / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def main() -> int:
    with TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "schema_drift.db"
        database_url = f"sqlite:///{db_path.as_posix()}"
        config = build_alembic_config(database_url)
        command.upgrade(config, "head")

        engine = create_engine(database_url)
        try:
            with engine.connect() as connection:
                context = MigrationContext.configure(
                    connection,
                    opts={
                        "compare_type": True,
                        "compare_server_default": False,
                        "target_metadata": SQLModel.metadata,
                        "render_as_batch": True,
                    },
                )
                diffs = compare_metadata(context, SQLModel.metadata)
        finally:
            engine.dispose()

        if diffs:
            print("Schema drift detected between Alembic head and SQLModel metadata:")
            for diff in diffs:
                print(f"- {diff!r}")
            return 1

        print("Schema drift check passed.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
