from __future__ import annotations

from pathlib import Path

from src.config.settings import Settings
from src.services.source_discovery_eval_service import SourceDiscoveryEvaluationService


def test_source_discovery_fixture_eval_runs(tmp_path: Path) -> None:
    settings = Settings(
        APP_ENV="test",
        SOURCE_DISCOVERY_DATABASE_URL=f"sqlite:///{(tmp_path / 'source_discovery.db').as_posix()}",
        WAVE_MONITOR_DATABASE_URL=f"sqlite:///{(tmp_path / 'wave.db').as_posix()}",
        SOURCE_DISCOVERY_EVAL_FIXTURE_PATH="./app/server/data/source_discovery_eval_fixtures.json",
    )
    service = SourceDiscoveryEvaluationService(settings)
    result = service.run_fixture_evaluation()

    assert result["metadata"]["eventCaseCount"] == 2
    assert result["metadata"]["reputationCaseCount"] == 3
    assert result["metrics"]["eventClusterPairwisePrecision"] >= 0.5
    assert result["metrics"]["reputationDirectionAccuracy"] >= 0.66
    assert "sourceClassFairnessSummary" in result["metrics"]
