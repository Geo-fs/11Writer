from __future__ import annotations

import json
import unicodedata
from itertools import combinations
from pathlib import Path
from typing import Any

from src.config.settings import Settings
from src.services.source_discovery_service import DEFAULT_REPUTATION_PROFILE, REPUTATION_PROFILES


class SourceDiscoveryEvaluationService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def load_fixture_manifest(self, path: str | None = None) -> dict[str, Any]:
        manifest_path = Path(path or self._settings.source_discovery_eval_fixture_path)
        if not manifest_path.exists():
            raise FileNotFoundError(f"Source Discovery evaluation manifest not found: {manifest_path}")
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Source Discovery evaluation manifest must be a JSON object.")
        return payload

    def run_fixture_evaluation(self, path: str | None = None, *, profile_name: str = DEFAULT_REPUTATION_PROFILE) -> dict[str, Any]:
        manifest = self.load_fixture_manifest(path)
        event_cases = manifest.get("eventCases", [])
        reputation_cases = manifest.get("reputationCases", [])
        challenge_sets = manifest.get("challengeSets", [])
        if not isinstance(event_cases, list) or not isinstance(reputation_cases, list):
            raise ValueError("Source Discovery evaluation manifest must include eventCases and reputationCases lists.")
        event_results = [self._evaluate_event_case(case) for case in event_cases if isinstance(case, dict)]
        reputation_results = [self._evaluate_reputation_case(case, profile_name=profile_name) for case in reputation_cases if isinstance(case, dict)]
        fairness_summary = _fairness_summary(reputation_results)
        challenge_results = [self._evaluate_challenge_case(case, profile_name=profile_name) for case in challenge_sets if isinstance(case, dict)]

        return {
            "metadata": {
                "manifestPath": str(Path(path or self._settings.source_discovery_eval_fixture_path)),
                "profileName": profile_name,
                "eventCaseCount": len(event_results),
                "reputationCaseCount": len(reputation_results),
                "challengeCaseCount": len(challenge_results),
                "mode": "fixture_eval",
            },
            "metrics": {
                "eventClusterPairwisePrecision": _mean([row["pairwisePrecision"] for row in event_results]),
                "eventClusterPairwiseRecall": _mean([row["pairwiseRecall"] for row in event_results]),
                "contestedEventDetectionAccuracy": _mean([1.0 if row["contestedMatch"] else 0.0 for row in event_results]),
                "openQuestionRecall": _mean([1.0 if row["openQuestionMatch"] else 0.0 for row in event_results]),
                "reputationDirectionAccuracy": _mean([1.0 if row["directionMatch"] else 0.0 for row in reputation_results]),
                "scoreBandAccuracy": _mean([1.0 if row["bandMatch"] else 0.0 for row in reputation_results]),
                "sourceClassFairnessSummary": fairness_summary,
                "challengeSetAccuracy": _mean([1.0 if row["passed"] else 0.0 for row in challenge_results]),
            },
            "eventResults": event_results,
            "reputationResults": reputation_results,
            "challengeResults": challenge_results,
        }

    def run_local_benchmark(self, path: str | None = None, *, profile_name: str = DEFAULT_REPUTATION_PROFILE) -> dict[str, Any]:
        manifest_path = path or self._settings.source_discovery_live_benchmark_manifest_path
        return self.run_fixture_evaluation(manifest_path, profile_name=profile_name)

    def _evaluate_event_case(self, case: dict[str, Any]) -> dict[str, Any]:
        claims = case.get("claims", [])
        expected = case.get("expected", {})
        if not isinstance(claims, list) or not isinstance(expected, dict):
            raise ValueError("Event evaluation cases require claims and expected.")
        predicted_labels: dict[str, str] = {}
        predicted_statuses: dict[str, str] = {}
        signature_members: dict[str, list[dict[str, Any]]] = {}
        for claim in claims:
            if not isinstance(claim, dict):
                continue
            claim_id = str(claim.get("claimId") or f"claim-{len(predicted_labels) + 1}")
            signature = _event_signature_local(
                claim_text=str(claim.get("claimText", "")),
                claim_type=str(claim.get("claimType", "state")),
                observed_at=_optional_str(claim.get("observedAt")),
                knowledge_node_id=_optional_str(claim.get("knowledgeNodeId")),
                scope_hints=claim.get("scopeHints", {}) if isinstance(claim.get("scopeHints"), dict) else {},
            )
            predicted_labels[claim_id] = signature
            signature_members.setdefault(signature, []).append(claim)
        for signature, members in signature_members.items():
            roles = {_event_role_local(_optional_str(row.get("outcome"))) for row in members}
            supporting = any(role in {"supporting", "provisional"} for role in roles)
            if "corrective" in roles:
                status = "corrected"
            elif "contradicting" in roles:
                status = "contested"
            elif "open_question" in roles and not supporting:
                status = "open_question"
            elif len({str(row.get("sourceId", "")) for row in members}) > 1:
                status = "corroborated"
            else:
                status = "single_source"
            predicted_statuses[signature] = status
        expected_labels = {str(item["claimId"]): str(item["clusterLabel"]) for item in expected.get("clusterLabels", []) if isinstance(item, dict) and "claimId" in item and "clusterLabel" in item}
        predicted_pairs = _pairwise_pairs(predicted_labels)
        expected_pairs = _pairwise_pairs(expected_labels)
        contested_count = sum(1 for status in predicted_statuses.values() if status in {"contested", "corrected"})
        open_question_count = sum(1 for status in predicted_statuses.values() if status == "open_question")
        return {
            "caseId": str(case.get("caseId", "event-case")),
            "predictedClusterCount": len(signature_members),
            "expectedClusterCount": int(expected.get("clusterCount", len(set(expected_labels.values())) or len(signature_members))),
            "pairwisePrecision": _pairwise_precision(predicted_pairs, expected_pairs),
            "pairwiseRecall": _pairwise_recall(predicted_pairs, expected_pairs),
            "contestedMatch": contested_count == int(expected.get("contestedCount", contested_count)),
            "openQuestionMatch": open_question_count == int(expected.get("openQuestionCount", open_question_count)),
            "predictedStatuses": predicted_statuses,
        }

    def _evaluate_reputation_case(self, case: dict[str, Any], *, profile_name: str) -> dict[str, Any]:
        expected = case.get("expected", {})
        if not isinstance(expected, dict):
            raise ValueError("Reputation evaluation cases require expected.")
        score = 0.5
        source_class = str(case.get("sourceClass", "unknown"))
        source_health = str(case.get("sourceHealth", "unknown"))
        outcomes = case.get("outcomes", [])
        if not isinstance(outcomes, list):
            outcomes = []
        profile = REPUTATION_PROFILES.get(profile_name, REPUTATION_PROFILES[DEFAULT_REPUTATION_PROFILE])
        for outcome in outcomes:
            if not isinstance(outcome, dict):
                continue
            score += _profile_delta_local(
                profile,
                source_class=source_class,
                source_health=source_health,
                outcome=str(outcome.get("outcome", "unresolved")),
                evidence_basis=str(outcome.get("evidenceBasis", "contextual")),
                corroborating_count=len(outcome.get("corroboratingSourceIds", [])) if isinstance(outcome.get("corroboratingSourceIds"), list) else 0,
                contradiction_count=len(outcome.get("contradictionSourceIds", [])) if isinstance(outcome.get("contradictionSourceIds"), list) else 0,
            )
        score = max(0.0, min(1.0, round(score, 4)))
        direction = "unchanged"
        if score > 0.5:
            direction = "increase"
        elif score < 0.5:
            direction = "decrease"
        band = _score_band(score)
        return {
            "caseId": str(case.get("caseId", "reputation-case")),
            "sourceClass": source_class,
            "predictedScore": score,
            "predictedDirection": direction,
            "predictedBand": band,
            "directionMatch": direction == str(expected.get("direction", direction)),
            "bandMatch": band == str(expected.get("scoreBand", band)),
        }

    def _evaluate_challenge_case(self, case: dict[str, Any], *, profile_name: str) -> dict[str, Any]:
        challenge_type = str(case.get("challengeType", "unknown"))
        reputation = self._evaluate_reputation_case(case, profile_name=profile_name)
        event = None
        if isinstance(case.get("claims"), list):
            event = self._evaluate_event_case(case)
        passed = reputation["directionMatch"] and reputation["bandMatch"]
        if event is not None:
            passed = passed and event["contestedMatch"] and event["openQuestionMatch"]
        return {
            "caseId": str(case.get("caseId", challenge_type)),
            "challengeType": challenge_type,
            "passed": bool(passed),
        }


def _normalize_text_local(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = " ".join(normalized.casefold().split())
    return normalized


def _event_signature_local(
    *,
    claim_text: str,
    claim_type: str,
    observed_at: str | None,
    knowledge_node_id: str | None,
    scope_hints: dict[str, Any],
) -> str:
    day = (observed_at or "")[:10]
    spatial = "|".join(sorted(str(item).casefold() for item in scope_hints.get("spatial", [])[:3])) if isinstance(scope_hints.get("spatial"), list) else ""
    topic = "|".join(sorted(str(item).casefold() for item in scope_hints.get("topic", [])[:3])) if isinstance(scope_hints.get("topic"), list) else ""
    return "||".join([
        claim_type.casefold().strip(),
        _normalize_text_local(claim_text),
        (knowledge_node_id or "").casefold().strip(),
        day.casefold().strip(),
        spatial,
        topic,
    ])


def _event_role_local(outcome: str | None) -> str:
    if outcome == "contradicted":
        return "contradicting"
    if outcome == "corrected":
        return "corrective"
    if outcome == "unresolved":
        return "open_question"
    return "supporting"


def _profile_delta_local(
    profile: dict[str, Any],
    *,
    source_class: str,
    source_health: str,
    outcome: str,
    evidence_basis: str,
    corroborating_count: int,
    contradiction_count: int,
) -> float:
    outcome_deltas = profile.get("outcome_deltas", {})
    source_bias = profile.get("source_class_bias", {})
    evidence_bias = profile.get("evidence_basis_bias", {})
    health_penalty = profile.get("health_penalty", {})
    delta = float(outcome_deltas.get(outcome, 0.0))
    delta += float(source_bias.get(source_class, 0.0))
    delta += float(evidence_bias.get(evidence_basis, 0.0))
    delta += min(corroborating_count, 3) * float(profile.get("corroboration_bonus", 0.0))
    delta += min(contradiction_count, 3) * float(profile.get("contradiction_penalty", 0.0))
    if outcome == "corrected":
        delta += float(profile.get("correction_penalty", 0.0))
    delta += float(health_penalty.get(source_health, 0.0))
    if outcome == "outdated" and source_class != "static":
        delta += float(profile.get("timeliness_penalty", 0.0))
    return delta


def _pairwise_pairs(labels: dict[str, str]) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for left, right in combinations(sorted(labels), 2):
        if labels[left] == labels[right]:
            pairs.add((left, right))
    return pairs


def _pairwise_precision(predicted: set[tuple[str, str]], expected: set[tuple[str, str]]) -> float:
    if not predicted:
        return 1.0 if not expected else 0.0
    return round(len(predicted & expected) / len(predicted), 4)


def _pairwise_recall(predicted: set[tuple[str, str]], expected: set[tuple[str, str]]) -> float:
    if not expected:
        return 1.0
    return round(len(predicted & expected) / len(expected), 4)


def _score_band(score: float) -> str:
    if score >= 0.67:
        return "high"
    if score >= 0.34:
        return "medium"
    return "low"


def _fairness_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    per_class: dict[str, list[dict[str, Any]]] = {}
    for row in results:
        per_class.setdefault(str(row.get("sourceClass", "unknown")), []).append(row)
    return {
        key: {
            "caseCount": len(values),
            "directionAccuracy": _mean([1.0 if item["directionMatch"] else 0.0 for item in values]),
            "scoreBandAccuracy": _mean([1.0 if item["bandMatch"] else 0.0 for item in values]),
            "meanPredictedScore": _mean([float(item["predictedScore"]) for item in values]),
        }
        for key, values in per_class.items()
    }


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 4)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
