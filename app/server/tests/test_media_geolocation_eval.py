from __future__ import annotations

from pathlib import Path

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
