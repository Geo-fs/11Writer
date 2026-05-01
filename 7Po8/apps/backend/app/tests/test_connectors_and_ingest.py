def test_connector_listing_and_sample_ingest(client) -> None:
    wave_response = client.post(
        "/api/waves",
        json={
            "name": "Keyword Watch",
            "description": "Track specific terms",
            "focus_type": "keyword",
        },
    )
    assert wave_response.status_code == 201
    wave_id = wave_response.json()["id"]

    connector_response = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "sample_news",
            "name": "News Stub Connector",
            "enabled": True,
            "polling_interval_minutes": 15,
            "config_json": {"keywords": ["airport", "runway"]},
        },
    )
    assert connector_response.status_code == 201

    connectors_response = client.get(f"/api/waves/{wave_id}/connectors")
    assert connectors_response.status_code == 200
    assert len(connectors_response.json()) == 1

    ingest_response = client.post(f"/api/waves/{wave_id}/ingest/sample")
    assert ingest_response.status_code == 201
    ingest_payload = ingest_response.json()
    assert ingest_payload["ingested_count"] == 2
    assert ingest_payload["executed_connectors"] == 1
    assert ingest_payload["successful_runs"] == 1
    assert ingest_payload["failed_runs"] == 0

    records_response = client.get(f"/api/waves/{wave_id}/records")
    assert records_response.status_code == 200
    records = records_response.json()
    assert len(records) == 2
    assert records[0]["source_type"] == "sample_news"


def test_connector_config_validation(client) -> None:
    wave_response = client.post(
        "/api/waves",
        json={
            "name": "Validation Wave",
            "description": "Connector validation",
            "focus_type": "keyword",
        },
    )
    wave_id = wave_response.json()["id"]

    bad_type = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "unknown_connector",
            "name": "Bad Type",
            "enabled": True,
            "polling_interval_minutes": 10,
            "config_json": {},
        },
    )
    assert bad_type.status_code == 422
    assert "Unknown connector type" in bad_type.json()["detail"]

    bad_config = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "sample_news",
            "name": "Bad Config",
            "enabled": True,
            "polling_interval_minutes": 10,
            "config_json": {"keywords": ["ok", ""]},
        },
    )
    assert bad_config.status_code == 422
    assert "Invalid config for 'sample_news'" in bad_config.json()["detail"]
