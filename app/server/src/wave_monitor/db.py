from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.orm import Session, sessionmaker

from src.reference.db import get_engine
from src.wave_monitor.models import WaveMonitorBase


def init_db(database_url: str) -> None:
    WaveMonitorBase.metadata.create_all(get_engine(database_url))


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
