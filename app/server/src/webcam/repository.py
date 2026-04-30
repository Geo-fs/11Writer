from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from src.types.api import (
    CameraSourceInventoryEntry,
    CameraSourceRegistryEntry,
    ReviewQueueIssue,
    ReviewQueueItem,
)
from src.types.entities import (
    CameraComplianceMetadata,
    CameraEntity,
    CameraFrameMetadata,
    CameraOrientationMetadata,
    CameraPositionMetadata,
    CameraReviewMetadata,
    DerivedField,
    HistorySummary,
    QualityMetadata,
)
from src.webcam.models import (
    CameraFrameORM,
    CameraHealthORM,
    CameraRecordORM,
    CameraReviewQueueORM,
    CameraSourceInventoryORM,
    CameraSourceInventoryRunORM,
    CameraSourceRunORM,
    CameraSourceORM,
)


@dataclass
class PersistedSourceUpdate:
    source: CameraSourceRegistryEntry
    detail: str
    credentials_configured: bool
    blocked_reason: str | None
    degraded_reason: str | None
    last_attempt_at: str | None
    last_success_at: str | None
    last_failure_at: str | None
    success_count: int
    failure_count: int
    warning_count: int
    last_camera_count: int
    next_refresh_at: str | None = None
    backoff_until: str | None = None
    retry_count: int = 0
    last_http_status: int | None = None
    last_started_at: str | None = None
    last_completed_at: str | None = None
    cadence_seconds: int | None = None
    cadence_reason: str | None = None


@dataclass
class CameraFrameUpdate:
    camera_id: str
    fetched_at: str
    captured_at: str | None
    source_frame_url: str | None
    frame_hash: str | None
    status: str
    width: int | None
    height: int | None
    age_seconds: int | None
    health_state: str
    degraded_reason: str | None
    blocked_reason: str | None
    next_frame_refresh_at: str | None
    backoff_until: str | None
    retry_count: int
    last_http_status: int | None
    last_metadata_refresh_at: str | None


@dataclass
class SourceRunRecord:
    source_key: str
    started_at: str
    completed_at: str | None
    status: str
    camera_count: int
    normalized_count: int
    partial_failure_count: int
    warning_count: int
    http_status: int | None
    error_text: str | None
    run_mode: str = "scheduled"
    frame_probe_count: int = 0
    frame_status_counts: dict[str, int] | None = None
    metadata_uncertainty_count: int = 0
    cadence_observation: str | None = None


@dataclass
class SourceInventoryRunRecord:
    source_key: str
    started_at: str
    completed_at: str | None
    status: str
    discovered_camera_count: int
    imported_camera_count: int
    detail: str | None


@dataclass
class SourceContributionStats:
    discovered_camera_count: int = 0
    usable_camera_count: int = 0
    direct_image_camera_count: int = 0
    viewer_only_camera_count: int = 0
    missing_coordinate_camera_count: int = 0
    uncertain_orientation_camera_count: int = 0
    review_queue_count: int = 0
    import_readiness: str = "inventory-only"
    last_import_outcome: str | None = None


class WebcamRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert_source_inventory(self, entry: CameraSourceInventoryEntry) -> None:
        record = self._session.get(CameraSourceInventoryORM, entry.key)
        if record is None:
            record = CameraSourceInventoryORM(source_key=entry.key)
            self._session.add(record)
        record.source_name = entry.source_name
        record.source_family = entry.source_family
        record.source_type = entry.source_type
        record.access_method = entry.access_method
        record.onboarding_state = entry.onboarding_state
        record.owner = entry.owner
        record.authentication = entry.authentication
        record.credentials_configured = entry.credentials_configured
        record.rate_limit_notes_json = json.dumps(entry.rate_limit_notes)
        record.coverage_geography = entry.coverage_geography
        record.coverage_states_json = json.dumps(entry.coverage_states)
        record.coverage_regions_json = json.dumps(entry.coverage_regions)
        record.provides_exact_coordinates = entry.provides_exact_coordinates
        record.provides_direction_text = entry.provides_direction_text
        record.provides_numeric_heading = entry.provides_numeric_heading
        record.provides_direct_image = entry.provides_direct_image
        record.provides_viewer_only = entry.provides_viewer_only
        record.supports_embed = entry.supports_embed
        record.supports_storage = entry.supports_storage
        record.attribution_text = entry.compliance.attribution_text
        record.attribution_url = entry.compliance.attribution_url
        record.terms_url = entry.compliance.terms_url
        record.license_summary = entry.compliance.license_summary
        record.requires_authentication = entry.compliance.requires_authentication
        record.compliance_review_required = entry.compliance.review_required
        record.provenance_notes_json = json.dumps(entry.compliance.provenance_notes)
        record.compliance_notes_json = json.dumps(entry.compliance.notes)
        record.source_quality_notes_json = json.dumps(entry.source_quality_notes)
        record.source_stability_notes_json = json.dumps(entry.source_stability_notes)
        record.page_structure = entry.page_structure
        record.likely_camera_count = entry.likely_camera_count
        record.compliance_risk = entry.compliance_risk
        record.extraction_feasibility = entry.extraction_feasibility
        record.endpoint_verification_status = entry.endpoint_verification_status
        record.candidate_endpoint_url = entry.candidate_endpoint_url
        record.machine_readable_endpoint_url = entry.machine_readable_endpoint_url
        record.last_endpoint_check_at = entry.last_endpoint_check_at
        record.last_endpoint_http_status = entry.last_endpoint_http_status
        record.last_endpoint_content_type = entry.last_endpoint_content_type
        record.last_endpoint_result = entry.last_endpoint_result
        record.last_endpoint_notes_json = json.dumps(entry.last_endpoint_notes)
        record.verification_caveat = entry.verification_caveat
        record.blocked_reason = entry.blocked_reason
        record.approximate_camera_count = entry.approximate_camera_count
        record.last_catalog_import_at = entry.last_catalog_import_at
        record.last_catalog_import_status = entry.last_catalog_import_status
        record.last_catalog_import_detail = entry.last_catalog_import_detail

    def record_source_inventory_run(self, run: SourceInventoryRunRecord) -> None:
        self._session.add(
            CameraSourceInventoryRunORM(
                source_key=run.source_key,
                started_at=run.started_at,
                completed_at=run.completed_at,
                status=run.status,
                discovered_camera_count=run.discovered_camera_count,
                imported_camera_count=run.imported_camera_count,
                detail=run.detail,
            )
        )
        self._session.flush()

    def upsert_source(self, update: PersistedSourceUpdate) -> None:
        source = self._session.get(CameraSourceORM, update.source.key)
        if source is None:
            source = CameraSourceORM(source_key=update.source.key)
            self._session.add(source)
        source.display_name = update.source.display_name
        source.owner = update.source.owner
        source.source_type = update.source.source_type
        source.coverage = update.source.coverage
        source.priority = update.source.priority
        source.enabled = update.source.enabled
        source.authentication = update.source.authentication
        source.default_refresh_interval_seconds = update.source.default_refresh_interval_seconds
        source.status = update.source.status
        source.detail = update.detail
        source.credentials_configured = update.credentials_configured
        source.blocked_reason = update.blocked_reason
        source.degraded_reason = update.degraded_reason
        source.review_required = update.source.review_required
        source.last_attempt_at = update.last_attempt_at
        source.last_success_at = update.last_success_at
        source.last_failure_at = update.last_failure_at
        source.last_started_at = update.last_started_at
        source.last_completed_at = update.last_completed_at
        source.next_refresh_at = update.next_refresh_at
        source.backoff_until = update.backoff_until
        source.retry_count = update.retry_count
        source.last_http_status = update.last_http_status
        source.cadence_seconds = update.cadence_seconds
        source.cadence_reason = update.cadence_reason
        source.success_count = update.success_count
        source.failure_count = update.failure_count
        source.warning_count = update.warning_count
        source.last_camera_count = update.last_camera_count
        source.notes_json = json.dumps(update.source.notes)
        source.attribution_text = update.source.compliance.attribution_text
        source.attribution_url = update.source.compliance.attribution_url
        source.terms_url = update.source.compliance.terms_url
        source.license_summary = update.source.compliance.license_summary
        source.requires_authentication = update.source.compliance.requires_authentication
        source.supports_embedding = update.source.compliance.supports_embedding
        source.supports_frame_storage = update.source.compliance.supports_frame_storage
        source.compliance_review_required = update.source.compliance.review_required
        source.provenance_notes_json = json.dumps(update.source.compliance.provenance_notes)
        source.compliance_notes_json = json.dumps(update.source.compliance.notes)

    def replace_cameras_for_source(
        self,
        source_key: str,
        cameras: list[CameraEntity],
        *,
        fetched_at: str,
        last_attempt_at: str | None,
        last_success_at: str | None,
        stale_after_seconds: int | None,
    ) -> None:
        self._session.flush()
        existing = {
            row.camera_id: row
            for row in self._session.execute(
                select(CameraRecordORM)
                .where(CameraRecordORM.source_key == source_key)
                .options(selectinload(CameraRecordORM.health))
            ).scalars()
        }

        seen_ids: set[str] = set()
        for camera in cameras:
            seen_ids.add(camera.id)
            record = existing.get(camera.id)
            if record is None:
                record = CameraRecordORM(camera_id=camera.id, source_key=source_key)
                self._session.add(record)
            self._apply_camera(record, camera)
            health = record.health or CameraHealthORM(camera_id=camera.id, source_key=source_key, health_state=camera.health_state or "healthy")
            record.health = health
            health.source_key = source_key
            health.health_state = camera.health_state or "healthy"
            health.last_attempt_at = last_attempt_at
            health.last_success_at = last_success_at
            health.last_failure_at = fetched_at if camera.health_state in {"degraded", "blocked"} else health.last_failure_at
            health.freshness_seconds = camera.frame.age_seconds
            health.stale_after_seconds = stale_after_seconds
            health.last_metadata_refresh_at = camera.last_metadata_refresh_at or fetched_at
            existing_failures = health.consecutive_failures or 0
            health.consecutive_failures = 0 if camera.health_state == "healthy" else max(1, existing_failures)
            health.next_frame_refresh_at = camera.next_frame_refresh_at
            health.backoff_until = camera.backoff_until
            health.retry_count = camera.retry_count or 0
            health.degraded_reason = camera.degraded_reason
            health.blocked_reason = camera.degraded_reason if camera.health_state == "blocked" else None
            health.last_http_status = camera.last_http_status

            if camera.frame.last_frame_at or camera.frame.image_url or camera.frame.viewer_url:
                self._session.add(
                    CameraFrameORM(
                        camera_id=camera.id,
                        fetched_at=fetched_at,
                        captured_at=camera.frame.last_frame_at,
                        source_frame_url=camera.frame.image_url or camera.frame.viewer_url,
                        frame_hash=None,
                        status=camera.frame.status,
                        width=camera.frame.width,
                        height=camera.frame.height,
                        age_seconds=camera.frame.age_seconds,
                    )
                )

        for camera_id, record in existing.items():
            if camera_id not in seen_ids:
                record.status = "inactive"
                record.health_state = "stale"
                if record.health:
                    record.health.health_state = "stale"
        self._session.flush()

    def record_source_run(self, run: SourceRunRecord) -> None:
        self._session.add(
            CameraSourceRunORM(
                source_key=run.source_key,
                started_at=run.started_at,
                completed_at=run.completed_at,
                run_mode=run.run_mode,
                status=run.status,
                camera_count=run.camera_count,
                normalized_count=run.normalized_count,
                partial_failure_count=run.partial_failure_count,
                warning_count=run.warning_count,
                frame_probe_count=run.frame_probe_count,
                frame_status_counts_json=json.dumps(run.frame_status_counts or {}),
                metadata_uncertainty_count=run.metadata_uncertainty_count,
                http_status=run.http_status,
                error_text=run.error_text,
                cadence_observation=run.cadence_observation,
            )
        )
        self._session.flush()

    def update_source_run_summary(
        self,
        *,
        source_key: str,
        started_at: str,
        run_mode: str,
        frame_probe_count: int,
        frame_status_counts: dict[str, int],
        metadata_uncertainty_count: int,
        cadence_observation: str | None,
    ) -> None:
        run = self._session.execute(
            select(CameraSourceRunORM)
            .where(CameraSourceRunORM.source_key == source_key)
            .where(CameraSourceRunORM.started_at == started_at)
            .where(CameraSourceRunORM.run_mode == run_mode)
        ).scalar_one_or_none()
        if run is None:
            return
        run.frame_probe_count = frame_probe_count
        run.frame_status_counts_json = json.dumps(frame_status_counts)
        run.metadata_uncertainty_count = metadata_uncertainty_count
        run.cadence_observation = cadence_observation
        self._session.flush()

    def update_camera_frame_metadata(self, update: CameraFrameUpdate) -> None:
        record = self._session.get(CameraRecordORM, update.camera_id)
        if record is None:
            return
        health = record.health
        if health is None:
            health = CameraHealthORM(camera_id=record.camera_id, source_key=record.source_key, health_state=update.health_state)
            record.health = health
        record.frame_status = update.status
        record.last_frame_at = update.captured_at or update.fetched_at
        record.last_metadata_refresh_at = update.last_metadata_refresh_at or record.last_metadata_refresh_at
        record.frame_width = update.width
        record.frame_height = update.height
        if update.source_frame_url:
            record.frame_image_url = update.source_frame_url if update.status == "live" else record.frame_image_url
            if record.frame_viewer_url is None and update.status == "viewer-page-only":
                record.frame_viewer_url = update.source_frame_url
        record.health_state = update.health_state
        record.degraded_reason = update.degraded_reason
        health.health_state = update.health_state
        health.last_attempt_at = update.fetched_at
        if update.health_state in {"healthy", "needs-review", "degraded"}:
            health.last_success_at = update.fetched_at
        if update.health_state in {"blocked", "degraded"} and update.degraded_reason:
            health.last_failure_at = update.fetched_at
        health.freshness_seconds = update.age_seconds
        health.last_metadata_refresh_at = update.last_metadata_refresh_at or health.last_metadata_refresh_at
        health.next_frame_refresh_at = update.next_frame_refresh_at
        health.backoff_until = update.backoff_until
        health.retry_count = update.retry_count
        health.degraded_reason = update.degraded_reason
        health.blocked_reason = update.blocked_reason
        health.last_http_status = update.last_http_status
        self._session.add(
            CameraFrameORM(
                camera_id=update.camera_id,
                fetched_at=update.fetched_at,
                captured_at=update.captured_at,
                source_frame_url=update.source_frame_url,
                frame_hash=update.frame_hash,
                status=update.status,
                width=update.width,
                height=update.height,
                age_seconds=update.age_seconds,
            )
        )
        self._session.flush()

    def replace_review_queue(self, items: list[ReviewQueueItem]) -> None:
        self._session.execute(delete(CameraReviewQueueORM))
        now = datetime.now(tz=timezone.utc).isoformat()
        for item in items:
            for issue in item.issues:
                self._session.add(
                    CameraReviewQueueORM(
                        camera_id=item.camera.id,
                        source_key=item.source_key,
                        priority=item.priority,
                        issue_category=issue.category,
                        reason=issue.reason,
                        required_action=issue.required_action,
                        context_json=json.dumps(item.context),
                        status="open",
                        created_at=now,
                        updated_at=now,
                    )
                )
        self._session.flush()

    def list_sources(self) -> list[CameraSourceRegistryEntry]:
        rows = self._session.execute(select(CameraSourceORM).order_by(CameraSourceORM.priority, CameraSourceORM.source_key)).scalars().all()
        latest_runs = self._latest_source_runs()
        contribution_stats = self._source_contribution_stats()
        return [
            self._source_entry_from_row(
                row,
                latest_run=latest_runs.get(row.source_key),
                contribution_stats=contribution_stats.get(row.source_key),
            )
            for row in rows
        ]

    def list_source_inventory(self) -> list[CameraSourceInventoryEntry]:
        rows = self._session.execute(
            select(CameraSourceInventoryORM).order_by(CameraSourceInventoryORM.onboarding_state, CameraSourceInventoryORM.source_name)
        ).scalars().all()
        contribution_stats = self._source_contribution_stats()
        entries: list[CameraSourceInventoryEntry] = []
        for row in rows:
            stats = contribution_stats.get(row.source_key, SourceContributionStats())
            entries.append(
                CameraSourceInventoryEntry(
                    key=row.source_key,
                    source_name=row.source_name,
                    source_family=row.source_family,
                    source_type=row.source_type,  # type: ignore[arg-type]
                    access_method=row.access_method,  # type: ignore[arg-type]
                    onboarding_state=row.onboarding_state,  # type: ignore[arg-type]
                    owner=row.owner,
                    authentication=row.authentication,  # type: ignore[arg-type]
                    credentials_configured=row.credentials_configured,
                    rate_limit_notes=_loads_list(row.rate_limit_notes_json),
                    coverage_geography=row.coverage_geography,
                    coverage_states=_loads_list(row.coverage_states_json),
                    coverage_regions=_loads_list(row.coverage_regions_json),
                    provides_exact_coordinates=row.provides_exact_coordinates,
                    provides_direction_text=row.provides_direction_text,
                    provides_numeric_heading=row.provides_numeric_heading,
                    provides_direct_image=row.provides_direct_image,
                    provides_viewer_only=row.provides_viewer_only,
                    supports_embed=row.supports_embed,
                    supports_storage=row.supports_storage,
                    compliance=CameraComplianceMetadata(
                        attribution_text=row.attribution_text,
                        attribution_url=row.attribution_url,
                        terms_url=row.terms_url,
                        license_summary=row.license_summary,
                        requires_authentication=row.requires_authentication,
                        supports_embedding=row.supports_embed,
                        supports_frame_storage=row.supports_storage,
                        review_required=row.compliance_review_required,
                        provenance_notes=_loads_list(row.provenance_notes_json),
                        notes=_loads_list(row.compliance_notes_json),
                    ),
                    source_quality_notes=_loads_list(row.source_quality_notes_json),
                    source_stability_notes=_loads_list(row.source_stability_notes_json),
                    page_structure=row.page_structure,  # type: ignore[arg-type]
                    likely_camera_count=row.likely_camera_count,
                    compliance_risk=row.compliance_risk,  # type: ignore[arg-type]
                    extraction_feasibility=row.extraction_feasibility,  # type: ignore[arg-type]
                    endpoint_verification_status=row.endpoint_verification_status,  # type: ignore[arg-type]
                    candidate_endpoint_url=row.candidate_endpoint_url,
                    machine_readable_endpoint_url=row.machine_readable_endpoint_url,
                    last_endpoint_check_at=row.last_endpoint_check_at,
                    last_endpoint_http_status=row.last_endpoint_http_status,
                    last_endpoint_content_type=row.last_endpoint_content_type,
                    last_endpoint_result=row.last_endpoint_result,
                    last_endpoint_notes=_loads_list(row.last_endpoint_notes_json),
                    verification_caveat=row.verification_caveat,
                    blocked_reason=row.blocked_reason,
                    approximate_camera_count=row.approximate_camera_count or stats.discovered_camera_count,
                    import_readiness=stats.import_readiness,  # type: ignore[arg-type]
                    discovered_camera_count=stats.discovered_camera_count,
                    usable_camera_count=stats.usable_camera_count,
                    direct_image_camera_count=stats.direct_image_camera_count,
                    viewer_only_camera_count=stats.viewer_only_camera_count,
                    missing_coordinate_camera_count=stats.missing_coordinate_camera_count,
                    uncertain_orientation_camera_count=stats.uncertain_orientation_camera_count,
                    review_queue_count=stats.review_queue_count,
                    last_catalog_import_at=row.last_catalog_import_at,
                    last_catalog_import_status=row.last_catalog_import_status,
                    last_catalog_import_detail=row.last_catalog_import_detail,
                    last_import_outcome=stats.last_import_outcome or row.last_catalog_import_status,
                )
            )
        return entries

    def list_cameras(self) -> list[CameraEntity]:
        rows = self._session.execute(
            select(CameraRecordORM)
            .options(
                selectinload(CameraRecordORM.health),
                selectinload(CameraRecordORM.source),
            )
            .order_by(CameraRecordORM.source_key, CameraRecordORM.state, CameraRecordORM.label)
        ).scalars().all()
        return [self._camera_from_row(row) for row in rows]

    def list_review_queue(self, *, limit: int) -> list[ReviewQueueItem]:
        rows = self._session.execute(
            select(CameraReviewQueueORM)
            .options(
                selectinload(CameraReviewQueueORM.camera).selectinload(CameraRecordORM.health),
                selectinload(CameraReviewQueueORM.camera).selectinload(CameraRecordORM.source),
            )
            .order_by(CameraReviewQueueORM.priority, CameraReviewQueueORM.source_key, CameraReviewQueueORM.camera_id)
        ).scalars().all()

        grouped: dict[str, list[CameraReviewQueueORM]] = {}
        for row in rows:
            grouped.setdefault(row.camera_id, []).append(row)

        items: list[ReviewQueueItem] = []
        for camera_id, issue_rows in grouped.items():
            camera_row = issue_rows[0].camera
            context = json.loads(issue_rows[0].context_json) if issue_rows[0].context_json else {}
            items.append(
                ReviewQueueItem(
                    queue_id=f"review:{camera_id}",
                    priority=issue_rows[0].priority,  # type: ignore[arg-type]
                    source_key=issue_rows[0].source_key,
                    camera=self._camera_from_row(camera_row),
                    issues=[
                        ReviewQueueIssue(
                            category=row.issue_category,
                            reason=row.reason,
                            required_action=row.required_action,
                        )
                        for row in issue_rows
                    ],
                    context={str(key): str(value) for key, value in context.items()},
                )
            )
        items.sort(key=lambda item: (0 if item.priority == "high" else 1 if item.priority == "medium" else 2, item.source_key, item.camera.label))
        return items[:limit]

    def _apply_camera(self, record: CameraRecordORM, camera: CameraEntity) -> None:
        record.source_key = camera.source
        record.source_camera_id = camera.source_camera_id
        record.label = camera.label
        record.owner = camera.owner
        record.state = camera.state
        record.county = camera.county
        record.region = camera.region
        record.roadway = camera.roadway
        record.direction = camera.direction
        record.location_description = camera.location_description
        record.latitude = camera.latitude
        record.longitude = camera.longitude
        record.altitude = camera.altitude
        record.heading = camera.heading
        record.status = camera.status
        record.feed_type = camera.feed_type
        record.access_policy = camera.access_policy
        record.external_url = camera.external_url
        record.confidence = camera.confidence
        record.position_kind = camera.position.kind
        record.position_confidence = camera.position.confidence
        record.position_source = camera.position.source
        record.position_notes_json = json.dumps(camera.position.notes)
        record.orientation_kind = camera.orientation.kind
        record.orientation_degrees = camera.orientation.degrees
        record.orientation_cardinal_direction = camera.orientation.cardinal_direction
        record.orientation_confidence = camera.orientation.confidence
        record.orientation_source = camera.orientation.source
        record.orientation_is_ptz = camera.orientation.is_ptz
        record.orientation_notes_json = json.dumps(camera.orientation.notes)
        record.frame_status = camera.frame.status
        record.frame_refresh_interval_seconds = camera.frame.refresh_interval_seconds
        record.frame_image_url = camera.frame.image_url
        record.frame_thumbnail_url = camera.frame.thumbnail_url
        record.frame_stream_url = camera.frame.stream_url
        record.frame_viewer_url = camera.frame.viewer_url
        record.frame_width = camera.frame.width
        record.frame_height = camera.frame.height
        record.last_frame_at = camera.frame.last_frame_at
        record.last_metadata_refresh_at = camera.last_metadata_refresh_at or camera.fetched_at
        record.health_state = camera.health_state
        record.degraded_reason = camera.degraded_reason
        record.review_status = camera.review.status
        record.review_reason = camera.review.reason
        record.review_required_actions_json = json.dumps(camera.review.required_actions)
        record.review_issue_categories_json = json.dumps(camera.review.issue_categories)
        record.nearest_reference_ref_id = camera.nearest_reference_ref_id
        record.reference_link_status = camera.reference_link_status
        record.link_candidate_count = camera.link_candidate_count or 0
        record.reference_hint_text = camera.reference_hint_text
        record.facility_code_hint = camera.facility_code_hint
        record.raw_payload_json = json.dumps(camera.metadata)

    def _source_entry_from_row(
        self,
        row: CameraSourceORM,
        *,
        latest_run: CameraSourceRunORM | None = None,
        contribution_stats: SourceContributionStats | None = None,
    ) -> CameraSourceRegistryEntry:
        stats = contribution_stats or SourceContributionStats()
        return CameraSourceRegistryEntry(
            key=row.source_key,
            display_name=row.display_name,
            owner=row.owner,
            source_type=row.source_type,  # type: ignore[arg-type]
            coverage=row.coverage,
            priority=row.priority,
            enabled=row.enabled,
            authentication=row.authentication,  # type: ignore[arg-type]
            default_refresh_interval_seconds=row.default_refresh_interval_seconds,
            notes=_loads_list(row.notes_json),
            compliance=CameraComplianceMetadata(
                attribution_text=row.attribution_text,
                attribution_url=row.attribution_url,
                terms_url=row.terms_url,
                license_summary=row.license_summary,
                requires_authentication=row.requires_authentication,
                supports_embedding=row.supports_embedding,
                supports_frame_storage=row.supports_frame_storage,
                review_required=row.compliance_review_required,
                provenance_notes=_loads_list(row.provenance_notes_json),
                notes=_loads_list(row.compliance_notes_json),
            ),
            status=row.status,  # type: ignore[arg-type]
            detail=row.detail,
            credentials_configured=row.credentials_configured,
            blocked_reason=row.blocked_reason,
            review_required=row.review_required,
            degraded_reason=row.degraded_reason,
            last_attempt_at=row.last_attempt_at,
            last_success_at=row.last_success_at,
            last_failure_at=row.last_failure_at,
            success_count=row.success_count,
            failure_count=row.failure_count,
            warning_count=row.warning_count,
            last_camera_count=row.last_camera_count,
            next_refresh_at=row.next_refresh_at,
            backoff_until=row.backoff_until,
            retry_count=row.retry_count,
            last_http_status=row.last_http_status,
            last_started_at=row.last_started_at,
            last_completed_at=row.last_completed_at,
            cadence_seconds=row.cadence_seconds,
            cadence_reason=row.cadence_reason,
            last_run_mode=latest_run.run_mode if latest_run is not None else None,
            last_validation_at=(latest_run.completed_at or latest_run.started_at) if latest_run is not None and latest_run.run_mode == "validation" else None,
            last_frame_probe_count=latest_run.frame_probe_count if latest_run is not None else None,
            last_frame_status_summary=_loads_int_dict(latest_run.frame_status_counts_json) if latest_run is not None else {},
            last_metadata_uncertainty_count=latest_run.metadata_uncertainty_count if latest_run is not None else None,
            last_cadence_observation=latest_run.cadence_observation if latest_run is not None else None,
            inventory_source_type=_inventory_type_for_runtime(row.source_type),
            access_method=None,
            onboarding_state="active" if row.credentials_configured else "approved",
            coverage_states=[],
            coverage_regions=[],
            provides_exact_coordinates=None,
            provides_direction_text=None,
            provides_numeric_heading=None,
            provides_direct_image=None,
            provides_viewer_only=None,
            supports_embed=row.supports_embedding,
            supports_storage=row.supports_frame_storage,
            approximate_camera_count=row.last_camera_count,
            import_readiness=stats.import_readiness,  # type: ignore[arg-type]
            discovered_camera_count=stats.discovered_camera_count,
            usable_camera_count=stats.usable_camera_count,
            direct_image_camera_count=stats.direct_image_camera_count,
            viewer_only_camera_count=stats.viewer_only_camera_count,
            missing_coordinate_camera_count=stats.missing_coordinate_camera_count,
            uncertain_orientation_camera_count=stats.uncertain_orientation_camera_count,
            review_queue_count=stats.review_queue_count,
            last_import_outcome=stats.last_import_outcome or row.status,
            source_quality_notes=[],
            source_stability_notes=[],
            page_structure=None,
            likely_camera_count=None,
            compliance_risk=None,
            extraction_feasibility=None,
        )

    def _latest_source_runs(self) -> dict[str, CameraSourceRunORM]:
        rows = self._session.execute(
            select(CameraSourceRunORM).order_by(CameraSourceRunORM.source_key, CameraSourceRunORM.run_id.desc())
        ).scalars().all()
        latest: dict[str, CameraSourceRunORM] = {}
        for row in rows:
            latest.setdefault(row.source_key, row)
        return latest

    def _source_contribution_stats(self) -> dict[str, SourceContributionStats]:
        stats: dict[str, SourceContributionStats] = {}

        def get_stats(source_key: str) -> SourceContributionStats:
            return stats.setdefault(source_key, SourceContributionStats())

        for row in self._session.execute(
            select(
                CameraRecordORM.source_key,
                CameraRecordORM.status,
                CameraRecordORM.frame_image_url,
                CameraRecordORM.frame_viewer_url,
                CameraRecordORM.position_kind,
                CameraRecordORM.orientation_kind,
                CameraRecordORM.health_state,
            )
        ):
            source_key, status, frame_image_url, frame_viewer_url, position_kind, orientation_kind, health_state = row
            source_stats = get_stats(source_key)
            source_stats.discovered_camera_count += 1
            if status == "active":
                source_stats.usable_camera_count += 1
            if frame_image_url:
                source_stats.direct_image_camera_count += 1
            elif frame_viewer_url:
                source_stats.viewer_only_camera_count += 1
            if position_kind == "unknown":
                source_stats.missing_coordinate_camera_count += 1
            if orientation_kind in {"approximate", "ptz", "unknown"}:
                source_stats.uncertain_orientation_camera_count += 1
            if health_state in {"degraded", "blocked"} and source_stats.last_import_outcome is None:
                source_stats.last_import_outcome = health_state

        for source_key, count in self._session.execute(
            select(CameraReviewQueueORM.source_key, CameraReviewQueueORM.camera_id)
        ):
            source_stats = get_stats(source_key)
            source_stats.review_queue_count += 1

        latest_inventory_runs: dict[str, CameraSourceInventoryRunORM] = {}
        for row in self._session.execute(
            select(CameraSourceInventoryRunORM).order_by(
                CameraSourceInventoryRunORM.source_key,
                CameraSourceInventoryRunORM.run_id.desc(),
            )
        ).scalars():
            latest_inventory_runs.setdefault(row.source_key, row)

        for source_key, run in latest_inventory_runs.items():
            source_stats = get_stats(source_key)
            source_stats.last_import_outcome = run.status
            if source_stats.discovered_camera_count == 0:
                source_stats.discovered_camera_count = run.imported_camera_count or run.discovered_camera_count

        inventory_rows = self._session.execute(select(CameraSourceInventoryORM)).scalars().all()
        for row in inventory_rows:
            source_stats = get_stats(row.source_key)
            if row.last_catalog_import_status and source_stats.last_import_outcome is None:
                source_stats.last_import_outcome = row.last_catalog_import_status
            if source_stats.discovered_camera_count == 0 and row.approximate_camera_count:
                source_stats.discovered_camera_count = row.approximate_camera_count
            source_stats.import_readiness = _derive_import_readiness(
                onboarding_state=row.onboarding_state,
                last_import_outcome=source_stats.last_import_outcome,
                discovered_camera_count=source_stats.discovered_camera_count,
                usable_camera_count=source_stats.usable_camera_count,
                viewer_only_camera_count=source_stats.viewer_only_camera_count,
                uncertain_orientation_camera_count=source_stats.uncertain_orientation_camera_count,
                review_queue_count=source_stats.review_queue_count,
            )

        return stats

    def _camera_from_row(self, row: CameraRecordORM) -> CameraEntity:
        metadata = _loads_dict(row.raw_payload_json)
        return CameraEntity(
            id=row.camera_id,
            type="camera",
            source=row.source_key,
            label=row.label,
            latitude=row.latitude,
            longitude=row.longitude,
            altitude=row.altitude,
            heading=row.heading,
            speed=None,
            timestamp=row.last_metadata_refresh_at or row.last_frame_at or "",
            observed_at=row.last_frame_at,
            fetched_at=row.last_metadata_refresh_at,
            status=row.status,
            source_detail=row.owner,
            external_url=row.external_url,
            confidence=row.confidence,
            history_available=False,
            canonical_ids=_canonical_ids(row),
            raw_identifiers={},
            quality=QualityMetadata(
                score=row.confidence,
                label=row.review_status,
                source_freshness_seconds=row.health.freshness_seconds if row.health else None,
                notes=[],
            ),
            derived_fields=[
                DerivedField(
                    name="coordinate_kind",
                    value=row.position_kind,
                    derived_from=row.position_source or "persisted camera metadata",
                    method="persisted-record",
                ),
                DerivedField(
                    name="orientation_kind",
                    value=row.orientation_kind,
                    derived_from=row.orientation_source or "persisted camera metadata",
                    method="persisted-record",
                ),
            ],
            history_summary=HistorySummary(kind="none", point_count=0, partial=False),
            metadata=metadata,
            camera_id=row.camera_id,
            source_camera_id=row.source_camera_id,
            owner=row.owner,
            state=row.state,
            county=row.county,
            region=row.region,
            roadway=row.roadway,
            direction=row.direction,
            location_description=row.location_description,
            feed_type=row.feed_type,  # type: ignore[arg-type]
            access_policy=row.access_policy,
            position=CameraPositionMetadata(
                kind=row.position_kind,  # type: ignore[arg-type]
                confidence=row.position_confidence,
                source=row.position_source,
                notes=_loads_list(row.position_notes_json),
            ),
            orientation=CameraOrientationMetadata(
                kind=row.orientation_kind,  # type: ignore[arg-type]
                degrees=row.orientation_degrees,
                cardinal_direction=row.orientation_cardinal_direction,
                confidence=row.orientation_confidence,
                source=row.orientation_source,
                is_ptz=row.orientation_is_ptz,
                notes=_loads_list(row.orientation_notes_json),
            ),
            frame=CameraFrameMetadata(
                status=row.frame_status,  # type: ignore[arg-type]
                refresh_interval_seconds=row.frame_refresh_interval_seconds,
                last_frame_at=row.last_frame_at,
                age_seconds=row.health.freshness_seconds if row.health else None,
                image_url=row.frame_image_url,
                thumbnail_url=row.frame_thumbnail_url,
                stream_url=row.frame_stream_url,
                viewer_url=row.frame_viewer_url,
                width=row.frame_width,
                height=row.frame_height,
            ),
            compliance=CameraComplianceMetadata(
                attribution_text=row.source.attribution_text,
                attribution_url=row.source.attribution_url,
                terms_url=row.source.terms_url,
                license_summary=row.source.license_summary,
                requires_authentication=row.source.requires_authentication,
                supports_embedding=row.source.supports_embedding,
                supports_frame_storage=row.source.supports_frame_storage,
                review_required=row.source.compliance_review_required,
                provenance_notes=_loads_list(row.source.provenance_notes_json),
                notes=_loads_list(row.source.compliance_notes_json),
            ),
            review=CameraReviewMetadata(
                status=row.review_status,  # type: ignore[arg-type]
                reason=row.review_reason,
                required_actions=_loads_list(row.review_required_actions_json),
                issue_categories=_loads_list(row.review_issue_categories_json),
            ),
            health_state=row.health_state,
            degraded_reason=row.degraded_reason,
            last_metadata_refresh_at=row.last_metadata_refresh_at,
            next_frame_refresh_at=row.health.next_frame_refresh_at if row.health else None,
            backoff_until=row.health.backoff_until if row.health else None,
            retry_count=row.health.retry_count if row.health else None,
            last_http_status=row.health.last_http_status if row.health else None,
            nearest_reference_ref_id=row.nearest_reference_ref_id,
            reference_link_status=row.reference_link_status,
            link_candidate_count=row.link_candidate_count,
            reference_hint_text=row.reference_hint_text,
            facility_code_hint=row.facility_code_hint,
        )


def _loads_list(value: str | None) -> list[str]:
    if not value:
        return []
    loaded = json.loads(value)
    return [str(item) for item in loaded] if isinstance(loaded, list) else []


def _loads_dict(value: str | None) -> dict[str, str]:
    if not value:
        return {}
    loaded = json.loads(value)
    return {str(key): str(val) for key, val in loaded.items()} if isinstance(loaded, dict) else {}


def _loads_int_dict(value: str | None) -> dict[str, int]:
    if not value:
        return {}
    loaded = json.loads(value)
    if not isinstance(loaded, dict):
        return {}
    result: dict[str, int] = {}
    for key, val in loaded.items():
        try:
            result[str(key)] = int(val)
        except (TypeError, ValueError):
            continue
    return result


def _canonical_ids(row: CameraRecordORM) -> dict[str, str]:
    ids: dict[str, str] = {}
    if row.camera_id:
        ids["cameraId"] = row.camera_id
    if row.source_camera_id:
        ids["sourceCameraId"] = row.source_camera_id
    return ids


def _inventory_type_for_runtime(source_type: str) -> str:
    mapping = {
        "official-dot": "official-dot-api",
        "official-511": "official-511-api",
        "aggregator-api": "public-webcam-api",
        "public-webcam": "public-camera-page",
    }
    return mapping.get(source_type, "public-camera-page")


def _derive_import_readiness(
    *,
    onboarding_state: str,
    last_import_outcome: str | None,
    discovered_camera_count: int,
    usable_camera_count: int,
    viewer_only_camera_count: int,
    uncertain_orientation_camera_count: int,
    review_queue_count: int,
) -> str:
    if last_import_outcome in {"running", "importing"}:
        return "actively-importing"
    if onboarding_state in {"candidate", "blocked", "unsupported"}:
        return "inventory-only"
    if discovered_camera_count <= 0:
        return "approved-unvalidated"
    if usable_camera_count <= 0:
        return "low-yield"
    review_ratio = review_queue_count / discovered_camera_count if discovered_camera_count else 0.0
    if discovered_camera_count > 0:
        viewer_ratio = viewer_only_camera_count / discovered_camera_count
        uncertain_ratio = uncertain_orientation_camera_count / discovered_camera_count
        if (
            review_ratio >= 0.5
            or viewer_ratio >= 0.8
            or uncertain_ratio >= 0.8
            or last_import_outcome in {"partial", "degraded", "blocked"}
        ):
            return "poor-quality"
    return "validated"
