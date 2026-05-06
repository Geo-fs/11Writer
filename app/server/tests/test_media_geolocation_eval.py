from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from src.config.settings import Settings
from src.services.media_geolocation_eval_service import MediaGeolocationEvaluationService


def test_media_geolocation_eval_harness_runs_repo_safe_fixture_manifest(tmp_path: Path) -> None:
    settings = Settings(
        APP_ENV="test",
        SOURCE_DISCOVERY_DATABASE_URL=f"sqlite:///{(tmp_path / 'source_discovery.db').as_posix()}",
        WAVE_MONITOR_DATABASE_URL=f"sqlite:///{(tmp_path / 'wave_monitor.db').as_posix()}",
        SOURCE_DISCOVERY_MEDIA_GEOLOCATION_EVAL_FIXTURE_PATH="./app/server/data/media_geolocation_eval_fixtures.json",
    )
    service = MediaGeolocationEvaluationService(settings)

    result = service.run_fixture_evaluation()

    assert result["metadata"]["caseCount"] >= 3
    assert result["metrics"]["top1HitRate25Km"] >= 0.66
    assert result["metrics"]["ocrCoordinateExtractionSuccess"] >= 0.66
    assert result["results"]
    assert all("latencyMs" in item for item in result["results"])


def test_media_geolocation_live_benchmark_harness_aggregates_engine_results(tmp_path: Path, monkeypatch) -> None:
    manifest_path = tmp_path / "live_manifest.json"
    manifest_path.write_text(
        """
        {
          "cases": [
            {
              "caseId": "test-live",
              "category": "urban_landmark",
              "sourceId": "benchmark:test-live",
              "pageUrl": "https://example.invalid/page",
              "imageUrl": "https://example.invalid/image.jpg",
              "candidateLabels": ["Tokyo", "Paris"],
              "expected": {
                "latitude": 35.0,
                "longitude": 139.0,
                "countryOrRegion": "Tokyo"
              },
              "engines": ["deterministic", "geoclip", "streetclip", "fusion"]
            },
            {
              "caseId": "test-live-2",
              "category": "natural_landscape",
              "sourceId": "benchmark:test-live-2",
              "pageUrl": "https://example.invalid/page-2",
              "imageUrl": "https://example.invalid/image-2.jpg",
              "candidateLabels": ["Tokyo", "Paris"],
              "expected": {
                "latitude": 35.0,
                "longitude": 139.0,
                "countryOrRegion": "Tokyo"
              },
              "engines": ["deterministic", "geoclip", "streetclip", "fusion"]
            }
          ]
        }
        """.strip(),
        encoding="utf-8",
    )
    settings = Settings(
        APP_ENV="test",
        SOURCE_DISCOVERY_DATABASE_URL=f"sqlite:///{(tmp_path / 'source_discovery.db').as_posix()}",
        WAVE_MONITOR_DATABASE_URL=f"sqlite:///{(tmp_path / 'wave_monitor.db').as_posix()}",
        SOURCE_DISCOVERY_MEDIA_GEOLOCATION_LIVE_BENCHMARK_MANIFEST_PATH=str(manifest_path),
    )
    service = MediaGeolocationEvaluationService(settings)

    def _fake_fetch_media_artifact(*args, **kwargs):
        del args, kwargs
        return (
            SimpleNamespace(
                artifact_path=str(tmp_path / "artifact.jpg"),
                metadata={"mimeTypeSniffed": "image/jpeg", "width": 640, "height": 480},
                observed_latitude=None,
                observed_longitude=None,
                exif_timestamp=None,
            ),
            1,
        )

    def _fake_geolocate_media_artifact(settings, **kwargs):
        del settings
        engine = kwargs["engine"]
        latitude = 35.0 if engine != "streetclip" else None
        longitude = 139.0 if engine != "streetclip" else None
        label = "Tokyo" if engine == "streetclip" else "35.0,139.0"
        return SimpleNamespace(
            status="completed",
            top_label=label,
            top_latitude=latitude,
            top_longitude=longitude,
            top_confidence=0.8,
            top_confidence_ceiling=0.85,
            candidates=[SimpleNamespace(latitude=latitude, longitude=longitude, label=label)],
            clue_packet=SimpleNamespace(
                coordinate_clues=[SimpleNamespace(latitude=35.0, longitude=139.0)],
                place_text_clues=[],
                script_language_clues=[],
                environment_clues=[],
                time_clues=[],
            ),
            engine_attempts=[SimpleNamespace(engine=engine, status="completed", model_name=None, warm_state="warm")],
            engine_agreement={"hasConflict": False},
        )

    monkeypatch.setattr("src.services.media_geolocation_eval_service.fetch_media_artifact", _fake_fetch_media_artifact)
    monkeypatch.setattr("src.services.media_geolocation_eval_service.geolocate_media_artifact", _fake_geolocate_media_artifact)

    result = service.run_live_benchmark()

    assert result["metadata"]["mode"] == "live_benchmark"
    assert result["metadata"]["caseCount"] == 2
    assert result["metadata"]["categoryCounts"] == {"natural_landscape": 1, "urban_landmark": 1}
    assert set(result["engines"].keys()) >= {"deterministic", "geoclip", "streetclip", "fusion"}
    assert result["engines"]["geoclip"]["metrics"]["top1HitRate25Km"] == 1.0
    assert "meanProfiledPredictMs" in result["engines"]["geoclip"]["metrics"]
    assert result["engines"]["geoclip"]["categoryMetrics"]["urban_landmark"]["top1HitRate25Km"] == 1.0
    assert result["engines"]["geoclip"]["categoryMetrics"]["natural_landscape"]["top1HitRate25Km"] == 1.0
    assert result["engines"]["streetclip"]["metrics"]["countryRegionAccuracy"] == 1.0
