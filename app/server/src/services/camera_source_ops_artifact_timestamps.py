from __future__ import annotations

from src.types.api import CameraSourceInventoryEntry, CameraSourceOpsArtifactTimestampSummary


def build_camera_source_ops_artifact_timestamps(
    inventory: CameraSourceInventoryEntry,
    *,
    sandbox_available: bool,
) -> list[CameraSourceOpsArtifactTimestampSummary]:
    return [
        _endpoint_evaluation_timestamp(inventory),
        _candidate_report_timestamp(inventory),
        _graduation_plan_timestamp(inventory),
        _sandbox_validation_timestamp(inventory, sandbox_available=sandbox_available),
    ]


def build_export_summary_timestamp(
    generated_at: str,
) -> CameraSourceOpsArtifactTimestampSummary:
    return CameraSourceOpsArtifactTimestampSummary(
        artifact_key="export-debug-summary",
        available=True,
        timestamp_status="generated-now",
        source_timestamp=generated_at,
        provenance="Generated at request time by the read-only source-ops export/debug summary helper.",
        caveat="This timestamp reflects summary generation time, not source validation time.",
    )


def _endpoint_evaluation_timestamp(
    inventory: CameraSourceInventoryEntry,
) -> CameraSourceOpsArtifactTimestampSummary:
    available = inventory.onboarding_state == "candidate" and bool(inventory.candidate_endpoint_url)
    if not available:
        return CameraSourceOpsArtifactTimestampSummary(
            artifact_key="endpoint-evaluation",
            available=False,
            timestamp_status="not-applicable",
            provenance="No candidate endpoint evaluation context is recorded for this source.",
            caveat="No endpoint-evaluation timestamp exists because the source is not in candidate endpoint-evaluation scope.",
        )
    if inventory.last_endpoint_check_at:
        return CameraSourceOpsArtifactTimestampSummary(
            artifact_key="endpoint-evaluation",
            available=True,
            timestamp_status="recorded",
            source_timestamp=inventory.last_endpoint_check_at,
            provenance="Stored endpoint evaluation metadata on the source inventory entry.",
            caveat="This is the last recorded endpoint-check timestamp only and does not prove validation.",
        )
    return CameraSourceOpsArtifactTimestampSummary(
        artifact_key="endpoint-evaluation",
        available=True,
        timestamp_status="missing",
        provenance="Candidate endpoint metadata exists, but no stored endpoint-check timestamp is recorded.",
        caveat="Treat endpoint freshness as unknown until a stored endpoint-check timestamp exists.",
    )


def _candidate_report_timestamp(
    inventory: CameraSourceInventoryEntry,
) -> CameraSourceOpsArtifactTimestampSummary:
    available = inventory.onboarding_state == "candidate" and bool(inventory.candidate_endpoint_url)
    if not available:
        return CameraSourceOpsArtifactTimestampSummary(
            artifact_key="candidate-endpoint-report",
            available=False,
            timestamp_status="not-applicable",
            provenance="Candidate endpoint report composition is unavailable for this source.",
            caveat="No candidate-report timestamp exists because the source lacks candidate endpoint scope.",
        )
    if inventory.last_endpoint_check_at:
        return CameraSourceOpsArtifactTimestampSummary(
            artifact_key="candidate-endpoint-report",
            available=True,
            timestamp_status="recorded",
            source_timestamp=inventory.last_endpoint_check_at,
            provenance="Composed from stored endpoint evaluation metadata using the last recorded endpoint-check timestamp.",
            caveat="Candidate endpoint report freshness is bounded by the stored endpoint-check timestamp.",
        )
    return CameraSourceOpsArtifactTimestampSummary(
        artifact_key="candidate-endpoint-report",
        available=True,
        timestamp_status="missing",
        provenance="Candidate endpoint report is composable, but no stored endpoint-check timestamp is recorded.",
        caveat="Treat candidate-report freshness as unknown until endpoint metadata includes a stored check time.",
    )


def _graduation_plan_timestamp(
    inventory: CameraSourceInventoryEntry,
) -> CameraSourceOpsArtifactTimestampSummary:
    available = inventory.onboarding_state == "candidate" and bool(inventory.candidate_endpoint_url)
    if not available:
        return CameraSourceOpsArtifactTimestampSummary(
            artifact_key="graduation-plan",
            available=False,
            timestamp_status="not-applicable",
            provenance="Graduation planning is unavailable because the source is outside candidate endpoint-planning scope.",
            caveat="No graduation-plan timestamp exists for sources without candidate planning inputs.",
        )
    return CameraSourceOpsArtifactTimestampSummary(
        artifact_key="graduation-plan",
        available=True,
        timestamp_status="missing",
        provenance="Graduation plans are composed at request time from stored candidate metadata and do not carry an independent stored timestamp.",
        caveat="Treat graduation-plan freshness as unknown unless a separate stored plan artifact is introduced later.",
    )


def _sandbox_validation_timestamp(
    inventory: CameraSourceInventoryEntry,
    *,
    sandbox_available: bool,
) -> CameraSourceOpsArtifactTimestampSummary:
    if not sandbox_available:
        return CameraSourceOpsArtifactTimestampSummary(
            artifact_key="sandbox-validation-report",
            available=False,
            timestamp_status="not-applicable",
            provenance="No sandbox validation path is recorded for this source.",
            caveat="No sandbox-validation timestamp exists because the source is not sandbox-importable.",
        )
    if inventory.last_sandbox_import_at:
        return CameraSourceOpsArtifactTimestampSummary(
            artifact_key="sandbox-validation-report",
            available=True,
            timestamp_status="recorded",
            source_timestamp=inventory.last_sandbox_import_at,
            provenance="Stored sandbox import metadata on the source inventory entry.",
            caveat="This is the last stored sandbox-import time only and does not prove validation or activation.",
        )
    return CameraSourceOpsArtifactTimestampSummary(
        artifact_key="sandbox-validation-report",
        available=True,
        timestamp_status="missing",
        provenance="Sandbox validation is available, but no stored sandbox-import timestamp is recorded.",
        caveat="Treat sandbox-validation freshness as unknown until a stored sandbox import time exists.",
    )
