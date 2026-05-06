from __future__ import annotations

from src.services.source_discovery_adversarial_eval_service import SourceDiscoveryAdversarialEvaluationService


def test_source_discovery_adversarial_fixture_eval_runs() -> None:
    service = SourceDiscoveryAdversarialEvaluationService()
    result = service.run_fixture_evaluation()

    assert result["metadata"]["caseCount"] == 4
    assert result["metrics"]["detectionRecall"] >= 0.66
    assert result["metrics"]["highRiskRecall"] >= 0.5
    assert result["metrics"]["benignAllowAccuracy"] >= 1.0
