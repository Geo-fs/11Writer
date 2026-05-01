from sqlmodel import Session, select

from app.api.deps import db
from app.models.connector import Connector
from app.models.record import Record


def test_wave_delete_cascades_connectors_and_records(client) -> None:
    wave_response = client.post(
        "/api/waves",
        json={"name": "Delete Cascade", "description": "cascade test", "focus_type": "keyword"},
    )
    wave_id = wave_response.json()["id"]

    connector_response = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "sample_news",
            "name": "Cascade Connector",
            "enabled": True,
            "polling_interval_minutes": 15,
            "config_json": {"keywords": ["airport"]},
        },
    )
    connector_id = connector_response.json()["id"]

    ingest_response = client.post(f"/api/waves/{wave_id}/ingest/sample")
    assert ingest_response.status_code == 201

    delete_response = client.delete(f"/api/waves/{wave_id}")
    assert delete_response.status_code == 204

    connector_lookup = client.patch(f"/api/connectors/{connector_id}", json={"enabled": False})
    assert connector_lookup.status_code == 404

    with Session(db.engine) as session:
        connector_count = session.exec(
            select(Connector).where(Connector.wave_id == wave_id)
        ).all()
        record_count = session.exec(select(Record).where(Record.wave_id == wave_id)).all()
    assert connector_count == []
    assert record_count == []
