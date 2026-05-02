from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session, sessionmaker

from src.reference.db import get_engine
from src.source_discovery.models import SourceDiscoveryBase


def init_db(database_url: str) -> None:
    engine = get_engine(database_url)
    SourceDiscoveryBase.metadata.create_all(engine)
    if database_url.startswith("sqlite"):
        _backfill_sqlite_columns(engine)


def _backfill_sqlite_columns(engine) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    statements = []
    if "source_reputation_events" in table_names:
        existing = {column["name"] for column in inspector.get_columns("source_reputation_events")}
        if "reversed_at" not in existing:
            statements.append("ALTER TABLE source_reputation_events ADD COLUMN reversed_at VARCHAR(64)")
        if "reversal_reason" not in existing:
            statements.append("ALTER TABLE source_reputation_events ADD COLUMN reversal_reason TEXT")
    if "source_memories" in table_names:
        memory_columns = {column["name"] for column in inspector.get_columns("source_memories")}
        if "canonical_url" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN canonical_url VARCHAR(1024)")
        if "domain_scope" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN domain_scope VARCHAR(255) DEFAULT 'unknown'")
        if "owner_lane" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN owner_lane VARCHAR(64)")
        if "next_check_at" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN next_check_at VARCHAR(64)")
        if "health_check_fail_count" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN health_check_fail_count INTEGER DEFAULT 0")
    if "source_scheduler_ticks" in table_names:
        tick_columns = {column["name"] for column in inspector.get_columns("source_scheduler_ticks")}
        if "record_extract_jobs_requested" not in tick_columns:
            statements.append("ALTER TABLE source_scheduler_ticks ADD COLUMN record_extract_jobs_requested INTEGER DEFAULT 0")
        if "record_extract_jobs_completed" not in tick_columns:
            statements.append("ALTER TABLE source_scheduler_ticks ADD COLUMN record_extract_jobs_completed INTEGER DEFAULT 0")
        if "llm_tasks_requested" not in tick_columns:
            statements.append("ALTER TABLE source_scheduler_ticks ADD COLUMN llm_tasks_requested INTEGER DEFAULT 0")
        if "llm_tasks_completed" not in tick_columns:
            statements.append("ALTER TABLE source_scheduler_ticks ADD COLUMN llm_tasks_completed INTEGER DEFAULT 0")
    if not statements:
        return
    if (
        "source_reputation_events" not in table_names
        and "source_memories" not in table_names
        and "source_scheduler_ticks" not in table_names
    ):
        return
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def get_session_factory(database_url: str) -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(database_url), autoflush=False, autocommit=False, future=True)


@contextmanager
def session_scope(database_url: str) -> Iterator[Session]:
    init_db(database_url)
    session = get_session_factory(database_url)()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
