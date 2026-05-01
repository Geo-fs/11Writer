from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.deps import db
from app.main import create_app


@pytest.fixture()
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    db_path = tmp_path / "test.db"
    db.reconfigure(f"sqlite:///{db_path}")
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
