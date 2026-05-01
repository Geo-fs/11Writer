from app.connectors.registry import registry
from app.connectors.weather import WeatherConfig, WeatherConnector


def _mock_weather_payload(config: WeatherConfig) -> dict:
    return {
        "_source_url": "https://api.open-meteo.com/v1/forecast?mock=1",
        "current": {
            "time": "2026-03-14T12:00:00Z",
            "temperature_2m": 34.2 if config.units == "metric" else 93.6,
            "wind_speed_10m": 45.0,
            "precipitation": 2.5,
            "weather_code": 95,
        },
    }


def _replace_weather_connector() -> None:
    registry.register(WeatherConnector(fetch_weather=_mock_weather_payload))


def test_weather_config_validation(client) -> None:
    _replace_weather_connector()
    wave_response = client.post(
        "/api/waves",
        json={"name": "Weather Validation", "description": "config test", "focus_type": "location"},
    )
    wave_id = wave_response.json()["id"]

    invalid_lat = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "weather",
            "name": "Weather",
            "enabled": True,
            "polling_interval_minutes": 20,
            "config_json": {"latitude": 999, "longitude": -97.74, "units": "metric"},
        },
    )
    assert invalid_lat.status_code == 422
    assert "Invalid config for 'weather'" in invalid_lat.json()["detail"]

    unknown_field = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "weather",
            "name": "Weather",
            "enabled": True,
            "polling_interval_minutes": 20,
            "config_json": {
                "latitude": 30.27,
                "longitude": -97.74,
                "units": "metric",
                "bogus": True,
            },
        },
    )
    assert unknown_field.status_code == 422
    assert "Invalid config for 'weather'" in unknown_field.json()["detail"]


def test_weather_ingestion_and_dedupe(client) -> None:
    _replace_weather_connector()
    wave_response = client.post(
        "/api/waves",
        json={"name": "Weather Ingest", "description": "ingest", "focus_type": "location"},
    )
    wave_id = wave_response.json()["id"]

    connector_response = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "weather",
            "name": "Austin Weather",
            "enabled": True,
            "polling_interval_minutes": 15,
            "config_json": {"latitude": 30.2672, "longitude": -97.7431, "units": "metric"},
        },
    )
    assert connector_response.status_code == 201

    ingest_one = client.post(f"/api/waves/{wave_id}/ingest/sample")
    assert ingest_one.status_code == 201
    assert ingest_one.json()["ingested_count"] == 1

    ingest_two = client.post(f"/api/waves/{wave_id}/ingest/sample")
    assert ingest_two.status_code == 201
    assert ingest_two.json()["ingested_count"] == 0

    records_response = client.get(f"/api/waves/{wave_id}/records")
    records = records_response.json()
    assert len(records) == 1
    assert records[0]["source_type"] == "weather"
    assert records[0]["latitude"] == 30.2672
    assert records[0]["longitude"] == -97.7431


def test_weather_threshold_signal(client) -> None:
    _replace_weather_connector()
    wave_response = client.post(
        "/api/waves",
        json={"name": "Weather Signals", "description": "thresholds", "focus_type": "location"},
    )
    wave_id = wave_response.json()["id"]

    connector_response = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "weather",
            "name": "Weather Alerts",
            "enabled": True,
            "polling_interval_minutes": 15,
            "config_json": {
                "latitude": 30.2672,
                "longitude": -97.7431,
                "units": "metric",
                "thresholds": {
                    "max_temperature": 30.0,
                    "max_wind_speed": 30.0,
                    "precipitation_trigger": True,
                    "severe_condition_keywords": ["thunderstorm"],
                },
            },
        },
    )
    connector_id = connector_response.json()["id"]

    ingest = client.post(f"/api/waves/{wave_id}/ingest/sample")
    assert ingest.status_code == 201

    connector_signals = client.get(f"/api/connectors/{connector_id}/signals")
    assert connector_signals.status_code == 200
    payload = connector_signals.json()
    threshold_signals = [
        signal for signal in payload if signal["type"] == "weather_threshold_crossed"
    ]
    assert len(threshold_signals) == 1
    assert threshold_signals[0]["severity"] in {"medium", "high"}


def test_weather_scheduler_integration(client) -> None:
    _replace_weather_connector()
    wave_response = client.post(
        "/api/waves",
        json={"name": "Weather Scheduler", "description": "scheduler", "focus_type": "location"},
    )
    wave_id = wave_response.json()["id"]

    connector_response = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "weather",
            "name": "Weather Scheduled",
            "enabled": True,
            "polling_interval_minutes": 15,
            "config_json": {"latitude": 30.2672, "longitude": -97.7431, "units": "metric"},
        },
    )
    connector_id = connector_response.json()["id"]

    tick = client.post("/api/scheduler/tick")
    assert tick.status_code == 200
    assert tick.json()["successful_runs"] >= 1

    runs = client.get(f"/api/connectors/{connector_id}/runs")
    assert runs.status_code == 200
    assert len(runs.json()) >= 1
