from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.services.source_discovery_service import _detect_adversarial_findings, _highest_adversarial_risk


DEFAULT_ADVERSARIAL_FIXTURE_PATH = Path("app/server/data/source_discovery_adversarial_fixtures.json")


class SourceDiscoveryAdversarialEvaluationService:
    def load_fixture_manifest(self, path: str | None = None) -> dict[str, Any]:
        manifest_path = Path(path) if path else DEFAULT_ADVERSARIAL_FIXTURE_PATH
        if not manifest_path.exists():
            raise FileNotFoundError(f"Source Discovery adversarial evaluation manifest not found: {manifest_path}")
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Source Discovery adversarial evaluation manifest must be a JSON object.")
        return payload

    def run_fixture_evaluation(self, path: str | None = None) -> dict[str, Any]:
        manifest = self.load_fixture_manifest(path)
        cases = manifest.get("cases", [])
        if not isinstance(cases, list):
            raise ValueError("Source Discovery adversarial evaluation manifest must include a cases list.")
        results = [self._evaluate_case(case) for case in cases if isinstance(case, dict)]
        risky_results = [row for row in results if row["expectedDetect"]]
        benign_results = [row for row in results if not row["expectedDetect"]]
        high_risk_results = [row for row in results if row["expectedRisk"] == "high"]
        return {
            "metadata": {
                "manifestPath": str(Path(path) if path else DEFAULT_ADVERSARIAL_FIXTURE_PATH),
                "caseCount": len(results),
                "mode": "fixture_eval",
            },
            "metrics": {
                "detectionRecall": _mean([1.0 if row["detectMatch"] else 0.0 for row in risky_results]),
                "highRiskRecall": _mean(
                    [1.0 if row["predictedRisk"] == "high" else 0.0 for row in high_risk_results]
                ),
                "benignAllowAccuracy": _mean([1.0 if row["detectMatch"] else 0.0 for row in benign_results]),
                "signalExpectationAccuracy": _mean([1.0 if row["signalMatch"] else 0.0 for row in results]),
            },
            "results": results,
        }

    def _evaluate_case(self, case: dict[str, Any]) -> dict[str, Any]:
        text = str(case.get("text", ""))
        url = str(case.get("url", "https://example.invalid"))
        expected = case.get("expected", {})
        if not isinstance(expected, dict):
            raise ValueError("Adversarial evaluation cases require an expected object.")
        findings = _detect_adversarial_findings(text, url=url)
        predicted_signals = sorted({finding["signal_type"] for finding in findings})
        predicted_risk = _highest_adversarial_risk([finding["risk_level"] for finding in findings])
        expected_signals = sorted({str(value) for value in expected.get("signals", []) if str(value).strip()})
        expected_detect = bool(expected.get("detect", False))
        return {
            "caseId": str(case.get("caseId", "adversarial-case")),
            "expectedDetect": expected_detect,
            "expectedRisk": str(expected.get("riskLevel", "none")),
            "expectedSignals": expected_signals,
            "predictedDetect": bool(findings),
            "predictedRisk": predicted_risk,
            "predictedSignals": predicted_signals,
            "detectMatch": bool(findings) == expected_detect,
            "riskMatch": predicted_risk == str(expected.get("riskLevel", "none")),
            "signalMatch": set(expected_signals).issubset(set(predicted_signals)),
        }


def _mean(values: list[float]) -> float:
    if not values:
        return 1.0
    return round(sum(values) / len(values), 4)
