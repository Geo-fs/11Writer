from collections.abc import Generator

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine


class DatabaseManager:
    def __init__(self, url: str) -> None:
        self._url = url
        self.engine = self._build_engine(url)

    def _build_engine(self, url: str) -> Engine:
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        engine = create_engine(url, connect_args=connect_args)
        if url.startswith("sqlite"):
            self._enable_sqlite_foreign_keys(engine)
        return engine

    @staticmethod
    def _enable_sqlite_foreign_keys(engine: Engine) -> None:
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:  # noqa: ARG001
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    def reconfigure(self, url: str) -> None:
        self._url = url
        self.engine = self._build_engine(url)

    def get_session(self) -> Generator[Session, None, None]:
        with Session(self.engine) as session:
            yield session

    def create_all(self) -> None:
        SQLModel.metadata.create_all(self.engine)
