from collections.abc import Generator

from sqlmodel import Session

from app.core.settings import settings
from app.db.session import DatabaseManager

db = DatabaseManager(settings.database_url)


def get_session() -> Generator[Session, None, None]:
    yield from db.get_session()
