from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha1
from typing import Any, Literal

import httpx

from src.adapters.base import Adapter
from src.config.settings import Settings
from src.services.camera_registry import get_camera_source_definition
from src.types.api import CameraSourceRegistryEntry
from src.types.entities import (
    CameraComplianceMetadata,
    CameraEntity,
    CameraFrameMetadata,
    CameraOrientationMetadata,
    CameraPositionMetadata,
    CameraReviewMetadata,
    DerivedField,
    QualityMetadata,
)


US_BBOX = (49.5, -66.5, 24.0, -125.0)
FetchState = Literal["healthy", "degraded", "rate-limited", "blocked", "credentials-missing", "needs-review"]


@dataclass(frozen=True)
class ConnectorIssue:
    category: str
    reason: str
    required_action: str


@dataclass(frozen=True)
class OrientationGuess:
    kind: str
    degrees: float | None
    cardinal_direction: str | None
    confidence: float | None
    is_ptz: bool
    notes: list[str]


@dataclass(frozen=True)
class CameraSourceFetchResult:
    source_key: str
    status: FetchState
    fetched_at: str
    cameras: list[CameraEntity]
    detail: str
    warnings: list[str]
    blocked_reason: str | None
    degraded_reason: str | None
    credentials_configured: bool
    review_required: bool
    total_records: int
    normalized_records: int
    partial_failure_count: int
    last_http_status: int | None


class CameraConnector(Adapter[CameraSourceFetchResult]):
    source_name: str

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def compliance(self) -> CameraComplianceMetadata:
        definition = get_camera_source_definition(self.source_name)
        if definition is None:
            raise RuntimeError(f"Missing source definition for {self.source_name}")
        return definition.compliance

    @property
    def source_definition(self) -> CameraSourceRegistryEntry:
        definition = get_camera_source_definition(self.source_name)
        if definition is None:
            raise RuntimeError(f"Missing source definition for {self.source_name}")
        return CameraSourceRegistryEntry(
            key=definition.key,
            display_name=definition.display_name,
            owner=definition.owner,
            source_type=definition.source_type,  # type: ignore[arg-type]
            coverage=definition.coverage,
            priority=definition.priority,
            enabled=True,
            authentication=definition.authentication,  # type: ignore[arg-type]
            default_refresh_interval_seconds=definition.default_refresh_interval_seconds,
            notes=list(definition.notes),
            compliance=definition.compliance,
            status="never-fetched",
            detail="Not fetched yet.",
        )

    async def fetch(self) -> CameraSourceFetchResult:
        raise NotImplementedError

    def _missing_credentials_result(self, detail: str) -> CameraSourceFetchResult:
        return CameraSourceFetchResult(
            source_key=self.source_name,
            status="credentials-missing",
            fetched_at=_now_iso(),
            cameras=[],
            detail=detail,
            warnings=[],
            blocked_reason=None,
            degraded_reason=detail,
            credentials_configured=False,
            review_required=self.compliance.review_required,
            total_records=0,
            normalized_records=0,
            partial_failure_count=0,
            last_http_status=None,
        )

    def _result_from_normalization(
        self,
        *,
        cameras: list[CameraEntity],
        warnings: list[str],
        total_records: int,
        partial_failure_count: int,
        detail: str,
        last_http_status: int | None,
    ) -> CameraSourceFetchResult:
        review_required = self.compliance.review_required or any(camera.review.status != "verified" for camera in cameras)
        if last_http_status == 429:
            status: FetchState = "rate-limited"
        elif last_http_status in {401, 403}:
            status = "blocked"
        elif partial_failure_count > 0 or warnings:
            status = "needs-review" if review_required else "degraded"
        elif review_required:
            status = "needs-review"
        else:
            status = "healthy"
        return CameraSourceFetchResult(
            source_key=self.source_name,
            status=status,
            fetched_at=_now_iso(),
            cameras=cameras,
            detail=detail,
            warnings=warnings,
            blocked_reason="Access blocked by upstream source." if status == "blocked" else None,
            degraded_reason="; ".join(warnings) if warnings else None,
            credentials_configured=True,
            review_required=review_required,
            total_records=total_records,
            normalized_records=len(cameras),
            partial_failure_count=partial_failure_count,
            last_http_status=last_http_status,
        )


class WsdotCameraConnector(CameraConnector):
    source_name = "wsdot-cameras"

    async def fetch(self) -> CameraSourceFetchResult:
        access_code = self._settings.wsdot_access_code
        if not access_code:
            return self._missing_credentials_result("WSDOT access code is missing.")

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{self._settings.wsdot_base_url}/GetCamerasAsJson",
                params={"AccessCode": access_code},
            )
            payload = _safe_json(response)

        items = payload if isinstance(payload, list) else []
        cameras: list[CameraEntity] = []
        warnings: list[str] = []
        failures = 0
        fetched_at = _now_iso()

        for item in items:
            normalized = self._normalize_item(item, fetched_at=fetched_at)
            if normalized is None:
                failures += 1
                continue
            if normalized.review.status != "verified":
                warnings.append(f"{normalized.label}: {normalized.review.reason or 'metadata requires review'}")
            cameras.append(normalized)

        return self._result_from_normalization(
            cameras=cameras,
            warnings=_dedupe(warnings),
            total_records=len(items),
            partial_failure_count=failures,
            detail="WSDOT camera metadata refreshed.",
            last_http_status=response.status_code,
        )

    def _normalize_item(self, item: Any, *, fetched_at: str) -> CameraEntity | None:
        if not isinstance(item, dict):
            return None
        latitude, longitude, position = _classify_position(
            source_fields=[item, item.get("CameraLocation") if isinstance(item.get("CameraLocation"), dict) else None],
            source_label="WSDOT camera coordinates",
        )
        if latitude is None or longitude is None:
            return None
        orientation = _classify_orientation(
            direction_text=_first_str(item, "Direction", "CameraDirection"),
            degrees=_first_float(item, "Heading", "Bearing"),
            source="WSDOT camera metadata",
        )
        image_url = _first_str(item, "ImageURL", "ImageUrl", "CameraURL")
        viewer_url = _first_str(item, "DisplayURL", "DisplayUrl", "Url")
        frame = _classify_frame(
            image_url=image_url,
            viewer_url=viewer_url,
            stream_url=None,
            width=_first_int(item, "ImageWidth", "Width"),
            height=_first_int(item, "ImageHeight", "Height"),
        )
        return _build_camera_entity(
            source=self.source_name,
            entity_id=f"camera:{self.source_name}:{_first_str(item, 'CameraID', 'Id', 'ID') or _hash_label(_first_str(item, 'Description', 'RoadName') or 'wsdot')}",
            label=_first_str(item, "Description", "Title", "DisplayName", "RoadName") or "WSDOT camera",
            latitude=latitude,
            longitude=longitude,
            fetched_at=fetched_at,
            external_url=viewer_url,
            camera_id=_first_str(item, "CameraID", "Id", "ID"),
            source_camera_id=_first_str(item, "CameraID", "Id", "ID"),
            owner="Washington State Department of Transportation",
            state="WA",
            county=_first_str(item, "County"),
            region=_first_str(item, "Region"),
            roadway=_first_str(item, "RoadName", "Route", "Highway"),
            direction=_first_str(item, "Direction", "CameraDirection"),
            location_description=_first_str(item, "Description", "CameraLocationDescription", "DisplayText"),
            feed_type="snapshot" if frame.image_url else "page",
            position=position,
            orientation=orientation,
            frame=frame,
            compliance=self.compliance,
            metadata={
                "rawRegion": _first_str(item, "Region"),
                "rawDirection": _first_str(item, "Direction", "CameraDirection"),
                "provider": "wsdot",
            },
        )


class OhgoCameraConnector(CameraConnector):
    source_name = "ohgo-cameras"

    async def fetch(self) -> CameraSourceFetchResult:
        api_key = self._settings.ohgo_api_key
        if not api_key:
            return self._missing_credentials_result("OHGO API key is missing.")

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{self._settings.ohgo_base_url}/cameras",
                headers={"Authorization": f"APIKEY {api_key}"},
                params={"api-key": api_key},
            )
            payload = _safe_json(response)

        items = payload.get("results") if isinstance(payload, dict) else []
        if not isinstance(items, list):
            items = []
        cameras: list[CameraEntity] = []
        warnings: list[str] = []
        failures = 0
        fetched_at = _now_iso()
        for item in items:
            site_results, site_failures = self._normalize_site(item, fetched_at=fetched_at)
            cameras.extend(site_results)
            failures += site_failures
            for camera in site_results:
                if camera.review.status != "verified":
                    warnings.append(f"{camera.label}: {camera.review.reason or 'metadata requires review'}")
        return self._result_from_normalization(
            cameras=cameras,
            warnings=_dedupe(warnings),
            total_records=len(items),
            partial_failure_count=failures,
            detail="OHGO camera metadata refreshed.",
            last_http_status=response.status_code,
        )

    def _normalize_site(self, item: Any, *, fetched_at: str) -> tuple[list[CameraEntity], int]:
        if not isinstance(item, dict):
            return [], 1
        latitude, longitude, position = _classify_position(
            source_fields=[item],
            source_label="OHGO site coordinates",
        )
        if latitude is None or longitude is None:
            return [], 1
        camera_views = item.get("CameraViews")
        if not isinstance(camera_views, list):
            return [], 1
        site_id = _first_str(item, "Id", "ID")
        results: list[CameraEntity] = []
        failures = 0
        for index, view in enumerate(camera_views):
            if not isinstance(view, dict):
                failures += 1
                continue
            orientation = _classify_orientation(
                direction_text=_first_str(view, "Direction"),
                degrees=_first_float(view, "Heading", "Bearing"),
                source="OHGO camera view metadata",
            )
            frame = _classify_frame(
                image_url=_first_str(view, "LargeUrl") or _first_str(view, "SmallUrl"),
                viewer_url=_redirect_link(item.get("Links")),
                stream_url=None,
                width=None,
                height=None,
            )
            camera = _build_camera_entity(
                source=self.source_name,
                entity_id=f"camera:{self.source_name}:{site_id or 'site'}:{index}",
                label=f"{_first_str(item, 'Location', 'Description') or 'OHGO camera'} [{_first_str(view, 'Direction') or f'view {index + 1}'}]",
                latitude=latitude,
                longitude=longitude,
                fetched_at=fetched_at,
                external_url=_redirect_link(item.get("Links")),
                camera_id=f"{site_id or 'site'}:{index}",
                source_camera_id=site_id,
                owner="Ohio Department of Transportation",
                state="OH",
                county=None,
                region=None,
                roadway=_first_str(view, "MainRoute"),
                direction=_first_str(view, "Direction"),
                location_description=_first_str(item, "Description", "Location"),
                feed_type="snapshot" if frame.image_url else "page",
                position=position,
                orientation=orientation,
                frame=frame,
                compliance=self.compliance,
                metadata={
                    "siteLocation": _first_str(item, "Location"),
                    "siteDescription": _first_str(item, "Description"),
                    "mainRoute": _first_str(view, "MainRoute"),
                    "provider": "ohgo",
                },
            )
            results.append(camera)
        return results, failures


class Wisconsin511CameraConnector(CameraConnector):
    source_name = "wisconsin-511-cameras"

    async def fetch(self) -> CameraSourceFetchResult:
        api_key = self._settings.wisconsin_511_api_key
        if not api_key:
            return self._missing_credentials_result("511 Wisconsin API key is missing.")

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{self._settings.wisconsin_511_base_url}/getcameras",
                params={"key": api_key, "format": "json"},
            )
            payload = _safe_json(response)

        items = payload if isinstance(payload, list) else []
        fetched_at = _now_iso()
        cameras: list[CameraEntity] = []
        warnings: list[str] = []
        failures = 0
        for item in items:
            normalized = self._normalize_item(item, fetched_at=fetched_at)
            if not normalized:
                failures += 1
                continue
            cameras.extend(normalized)
            for camera in normalized:
                if camera.review.status != "verified":
                    warnings.append(f"{camera.label}: {camera.review.reason or 'metadata requires review'}")
        return self._result_from_normalization(
            cameras=cameras,
            warnings=_dedupe(warnings),
            total_records=len(items),
            partial_failure_count=failures,
            detail="511 Wisconsin camera metadata refreshed.",
            last_http_status=response.status_code,
        )

    def _normalize_item(self, item: Any, *, fetched_at: str) -> list[CameraEntity] | None:
        if not isinstance(item, dict):
            return None
        latitude, longitude, position = _classify_position([item], "511 Wisconsin camera coordinates")
        if latitude is None or longitude is None:
            return None
        views = item.get("Views")
        if not isinstance(views, list) or not views:
            views = [None]
        results: list[CameraEntity] = []
        for index, view in enumerate(views):
            view_data = view if isinstance(view, dict) else {}
            orientation = _classify_orientation(
                direction_text=_first_str(item, "Direction"),
                degrees=None,
                source="511 Wisconsin direction text",
            )
            frame = _classify_frame(
                image_url=None,
                viewer_url=_first_str(view_data, "Url"),
                stream_url=None,
                width=None,
                height=None,
            )
            results.append(
                _build_camera_entity(
                    source=self.source_name,
                    entity_id=f"camera:{self.source_name}:{_first_str(item, 'Id', 'ID', 'SourceId') or 'site'}:{_first_str(view_data, 'Id') or index}",
                    label=_first_str(item, "Name", "Location") or "511WI camera",
                    latitude=latitude,
                    longitude=longitude,
                    fetched_at=fetched_at,
                    external_url=_first_str(view_data, "Url"),
                    camera_id=f"{_first_str(item, 'Id', 'ID', 'SourceId') or 'site'}:{_first_str(view_data, 'Id') or index}",
                    source_camera_id=_first_str(item, "Id", "ID", "SourceId"),
                    owner="Wisconsin Department of Transportation",
                    state="WI",
                    county=_first_str(item, "County"),
                    region=_first_str(item, "RegionName", "Region"),
                    roadway=_first_str(item, "Roadway", "RoadwayName"),
                    direction=_first_str(item, "Direction"),
                    location_description=_first_str(item, "Location"),
                    feed_type="page",
                    position=position,
                    orientation=orientation,
                    frame=frame,
                    compliance=self.compliance,
                    metadata={
                        "viewStatus": _first_str(view_data, "Status"),
                        "provider": "511wi",
                    },
                )
            )
        return results


class Georgia511CameraConnector(CameraConnector):
    source_name = "georgia-511-cameras"

    async def fetch(self) -> CameraSourceFetchResult:
        api_key = self._settings.georgia_511_api_key
        if not api_key:
            return self._missing_credentials_result("511 Georgia API key is missing.")

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{self._settings.georgia_511_base_url}/get/cameras",
                params={"key": api_key, "format": "json"},
            )
            payload = _safe_json(response)

        items = payload if isinstance(payload, list) else []
        fetched_at = _now_iso()
        cameras: list[CameraEntity] = []
        warnings: list[str] = []
        failures = 0
        for item in items:
            normalized = self._normalize_item(item, fetched_at=fetched_at)
            if not normalized:
                failures += 1
                continue
            cameras.extend(normalized)
            for camera in normalized:
                if camera.review.status != "verified":
                    warnings.append(f"{camera.label}: {camera.review.reason or 'metadata requires review'}")
        return self._result_from_normalization(
            cameras=cameras,
            warnings=_dedupe(warnings),
            total_records=len(items),
            partial_failure_count=failures,
            detail="511 Georgia camera metadata refreshed.",
            last_http_status=response.status_code,
        )

    def _normalize_item(self, item: Any, *, fetched_at: str) -> list[CameraEntity] | None:
        if not isinstance(item, dict):
            return None
        latitude, longitude, position = _classify_position([item], "511 Georgia camera coordinates")
        if latitude is None or longitude is None:
            return None
        views = item.get("Views")
        if not isinstance(views, list) or not views:
            views = [None]
        results: list[CameraEntity] = []
        for index, view in enumerate(views):
            view_data = view if isinstance(view, dict) else {}
            orientation = _classify_orientation(
                direction_text=_first_str(item, "Direction"),
                degrees=None,
                source="511 Georgia direction text",
            )
            frame = _classify_frame(
                image_url=None,
                viewer_url=_first_str(view_data, "Url"),
                stream_url=None,
                width=None,
                height=None,
            )
            results.append(
                _build_camera_entity(
                    source=self.source_name,
                    entity_id=f"camera:{self.source_name}:{_first_str(item, 'Id', 'SourceId') or 'site'}:{_first_str(view_data, 'Id') or index}",
                    label=_first_str(item, "Name", "Location") or "511GA camera",
                    latitude=latitude,
                    longitude=longitude,
                    fetched_at=fetched_at,
                    external_url=_first_str(view_data, "Url"),
                    camera_id=f"{_first_str(item, 'Id', 'SourceId') or 'site'}:{_first_str(view_data, 'Id') or index}",
                    source_camera_id=_first_str(item, "Id", "SourceId"),
                    owner="Georgia Department of Transportation",
                    state="GA",
                    county=None,
                    region=None,
                    roadway=_first_str(item, "Roadway"),
                    direction=_first_str(item, "Direction"),
                    location_description=_first_str(item, "Location"),
                    feed_type="page",
                    position=position,
                    orientation=orientation,
                    frame=frame,
                    compliance=self.compliance,
                    metadata={
                        "sourceName": _first_str(item, "Source"),
                        "sourceId": _first_str(item, "SourceId"),
                        "viewStatus": _first_str(view_data, "Status"),
                        "provider": "511ga",
                    },
                )
            )
        return results


def _normalize_structured_511_item(
    item: Any,
    *,
    fetched_at: str,
    source_name: str,
    owner: str,
    state: str,
    compliance: CameraComplianceMetadata,
    provider: str,
) -> list[CameraEntity] | None:
    if not isinstance(item, dict):
        return None
    latitude, longitude, position = _classify_position([item], f"{owner} camera coordinates")
    if latitude is None or longitude is None:
        return None
    views = item.get("Views")
    if not isinstance(views, list) or not views:
        views = [None]
    results: list[CameraEntity] = []
    for index, view in enumerate(views):
        view_data = view if isinstance(view, dict) else {}
        orientation = _classify_orientation(
            direction_text=_first_str(item, "Direction", "DirectionOfTravel"),
            degrees=None,
            source=f"{owner} direction text",
        )
        frame = _classify_frame(
            image_url=None,
            viewer_url=_first_str(view_data, "Url", "URL"),
            stream_url=None,
            width=None,
            height=None,
        )
        results.append(
            _build_camera_entity(
                source=source_name,
                entity_id=(
                    f"camera:{source_name}:{_first_str(item, 'Id', 'ID', 'SourceId') or 'site'}:"
                    f"{_first_str(view_data, 'Id', 'ID') or index}"
                ),
                label=_first_str(item, "Name", "Location") or f"{owner} camera",
                latitude=latitude,
                longitude=longitude,
                fetched_at=fetched_at,
                external_url=_first_str(view_data, "Url", "URL"),
                camera_id=f"{_first_str(item, 'Id', 'ID', 'SourceId') or 'site'}:{_first_str(view_data, 'Id', 'ID') or index}",
                source_camera_id=_first_str(item, "Id", "ID", "SourceId"),
                owner=owner,
                state=state,
                county=_first_str(item, "County"),
                region=_first_str(item, "RegionName", "Region"),
                roadway=_first_str(item, "Roadway", "RoadwayName"),
                direction=_first_str(item, "Direction", "DirectionOfTravel"),
                location_description=_first_str(item, "Location", "Name"),
                feed_type="page",
                position=position,
                orientation=orientation,
                frame=frame,
                compliance=compliance,
                metadata={
                    "viewStatus": _first_str(view_data, "Status"),
                    "provider": provider,
                },
            )
        )
    return results


def _normalize_ashcam_item(
    item: Any,
    *,
    fetched_at: str,
    source_name: str,
    owner: str,
    compliance: CameraComplianceMetadata,
) -> CameraEntity | None:
    if not isinstance(item, dict):
        return None
    latitude, longitude, position = _classify_position([item], "USGS Ashcam coordinates")
    if latitude is None or longitude is None:
        return None

    orientation = _classify_orientation(
        direction_text=None,
        degrees=_first_float(item, "bearingDeg"),
        source="USGS Ashcam bearing metadata",
    )
    newest = item.get("newestImage") if isinstance(item.get("newestImage"), dict) else {}
    frame = _classify_frame(
        image_url=_first_str(item, "currentImageUrl", "currentMediumImageUrl") or _first_str(newest, "imageUrl"),
        viewer_url=_first_str(item, "externalUrl"),
        stream_url=None,
        width=None,
        height=None,
    )
    volcano_name = _first_str(item, "vName")
    location_description = _first_str(item, "webcamName")
    return _build_camera_entity(
        source=source_name,
        entity_id=f"camera:{source_name}:{_first_str(item, 'webcamCode') or _hash_label(location_description or 'ashcam')}",
        label=location_description or "USGS Ashcam webcam",
        latitude=latitude,
        longitude=longitude,
        fetched_at=fetched_at,
        external_url=_first_str(item, "externalUrl"),
        camera_id=_first_str(item, "webcamCode"),
        source_camera_id=_first_str(item, "webcamCode"),
        owner=owner,
        state=None,
        county=None,
        region=volcano_name,
        roadway=None,
        direction=None,
        location_description=location_description,
        feed_type="snapshot" if frame.image_url else "page",
        position=position,
        orientation=orientation,
        frame=frame,
        compliance=compliance,
        metadata={
            "volcanoNumber": _first_str(item, "vnum"),
            "volcanoName": volcano_name,
            "faaIndicator": _first_str(item, "faaInd"),
            "hasImages": _first_str(item, "hasImages"),
            "provider": "usgs-ashcam",
        },
        reference_hint_text=volcano_name or location_description,
        facility_code_hint=_bookmark_code(_first_str(item, "externalUrl")),
    )


class Structured511CameraConnector(CameraConnector):
    def __init__(
        self,
        settings: Settings,
        *,
        source_name: str,
        owner: str,
        state: str,
        provider_label: str,
        base_url: str,
        api_key: str | None,
    ) -> None:
        super().__init__(settings)
        self.source_name = source_name
        self._owner = owner
        self._state = state
        self._provider_label = provider_label
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

    async def fetch(self) -> CameraSourceFetchResult:
        if not self._api_key:
            return self._missing_credentials_result(f"{self._provider_label} API key is missing.")

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{self._base_url}/get/cameras",
                params={"key": self._api_key, "format": "json"},
            )
            payload = _safe_json(response)

        items = payload if isinstance(payload, list) else []
        fetched_at = _now_iso()
        cameras: list[CameraEntity] = []
        warnings: list[str] = []
        failures = 0
        for item in items:
            normalized = _normalize_structured_511_item(
                item,
                fetched_at=fetched_at,
                source_name=self.source_name,
                owner=self._owner,
                state=self._state,
                compliance=self.compliance,
                provider=self._provider_label.lower().replace(" ", ""),
            )
            if not normalized:
                failures += 1
                continue
            cameras.extend(normalized)
            for camera in normalized:
                if camera.review.status != "verified":
                    warnings.append(f"{camera.label}: {camera.review.reason or 'metadata requires review'}")
        return self._result_from_normalization(
            cameras=cameras,
            warnings=_dedupe(warnings),
            total_records=len(items),
            partial_failure_count=failures,
            detail=f"{self._provider_label} camera metadata refreshed.",
            last_http_status=response.status_code,
        )


class UsgsAshcamConnector(CameraConnector):
    source_name = "usgs-ashcam"

    async def fetch(self) -> CameraSourceFetchResult:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self._settings.usgs_ashcam_base_url}/webcams")
            payload = _safe_json(response)

        items = payload.get("webcams") if isinstance(payload, dict) else []
        if not isinstance(items, list):
            items = []

        fetched_at = _now_iso()
        cameras: list[CameraEntity] = []
        warnings: list[str] = []
        failures = 0
        for item in items:
            normalized = _normalize_ashcam_item(
                item,
                fetched_at=fetched_at,
                source_name=self.source_name,
                owner="U.S. Geological Survey",
                compliance=self.compliance,
            )
            if normalized is None:
                failures += 1
                continue
            if normalized.review.status != "verified":
                warnings.append(f"{normalized.label}: {normalized.review.reason or 'metadata requires review'}")
            cameras.append(normalized)

        return self._result_from_normalization(
            cameras=cameras,
            warnings=_dedupe(warnings),
            total_records=len(items),
            partial_failure_count=failures,
            detail="USGS Ashcam webcam metadata refreshed.",
            last_http_status=response.status_code,
        )


class WindyWebcamConnector(CameraConnector):
    source_name = "windy-webcams"

    async def fetch(self) -> CameraSourceFetchResult:
        api_key = self._settings.windy_webcams_api_key
        if not api_key:
            return self._missing_credentials_result("Windy Webcams API key is missing.")

        north, east, south, west = US_BBOX
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.get(
                f"{self._settings.windy_webcams_base_url}/webcams",
                headers={"x-windy-api-key": api_key},
                params={
                    "bbox": f"{north},{east},{south},{west}",
                    "limit": 200,
                    "offset": 0,
                    "include": "location,images,urls,player,title",
                },
            )
            payload = _safe_json(response)

        items = _extract_windy_webcams(payload)
        fetched_at = _now_iso()
        cameras: list[CameraEntity] = []
        warnings: list[str] = []
        failures = 0
        for item in items:
            normalized = self._normalize_item(item, fetched_at=fetched_at)
            if normalized is None:
                failures += 1
                continue
            if normalized.review.status != "verified":
                warnings.append(f"{normalized.label}: {normalized.review.reason or 'metadata requires review'}")
            cameras.append(normalized)
        return self._result_from_normalization(
            cameras=cameras,
            warnings=_dedupe(warnings),
            total_records=len(items),
            partial_failure_count=failures,
            detail="Windy webcam metadata refreshed.",
            last_http_status=response.status_code,
        )

    def _normalize_item(self, item: Any, *, fetched_at: str) -> CameraEntity | None:
        if not isinstance(item, dict):
            return None
        location = item.get("location")
        if not isinstance(location, dict):
            return None
        latitude, longitude, position = _classify_position([location], "Windy webcam location metadata")
        if latitude is None or longitude is None:
            return None
        image_url = _windy_image_url(item.get("images"))
        viewer_url = _first_nested_str(item.get("urls"), ("detail", "href"), ("web", "href")) or _first_str(item, "url")
        stream_url = _first_nested_str(item.get("player"), ("live", "embed"))
        frame = _classify_frame(
            image_url=image_url,
            viewer_url=viewer_url,
            stream_url=stream_url,
            width=None,
            height=None,
        )
        orientation = _classify_orientation(
            direction_text=None,
            degrees=None,
            source="Windy webcam listing does not provide trustworthy orientation metadata",
        )
        return _build_camera_entity(
            source=self.source_name,
            entity_id=f"camera:{self.source_name}:{_first_str(item, 'id', 'webcamId') or _hash_label(_first_str(item, 'title', 'name') or 'windy')}",
            label=_first_str(item, "title", "name") or "Windy webcam",
            latitude=latitude,
            longitude=longitude,
            fetched_at=fetched_at,
            external_url=viewer_url,
            camera_id=_first_str(item, "id", "webcamId"),
            source_camera_id=_first_str(item, "id", "webcamId"),
            owner=_first_str(item, "operator") or "Windy.com / upstream webcam operator",
            state=_first_str(location, "state"),
            county=None,
            region=_first_str(location, "region"),
            roadway=None,
            direction=None,
            location_description=_first_str(location, "city", "region"),
            feed_type="snapshot" if image_url else "page",
            position=position,
            orientation=orientation,
            frame=frame,
            compliance=self.compliance.model_copy(
                update={
                    "review_required": True,
                    "notes": self.compliance.notes + ["Operator-specific permissions may require manual compliance review."],
                }
            ),
            metadata={
                "country": _first_str(location, "country"),
                "operator": _first_str(item, "operator"),
                "provider": "windy",
            },
        )


def build_camera_connectors(settings: Settings) -> list[CameraConnector]:
    return [
        WsdotCameraConnector(settings),
        OhgoCameraConnector(settings),
        Wisconsin511CameraConnector(settings),
        Georgia511CameraConnector(settings),
        Structured511CameraConnector(
            settings,
            source_name="511ny-cameras",
            owner="New York State 511",
            state="NY",
            provider_label="511NY",
            base_url=settings.newyork_511_base_url,
            api_key=settings.newyork_511_api_key,
        ),
        Structured511CameraConnector(
            settings,
            source_name="idaho-511-cameras",
            owner="Idaho Transportation Department",
            state="ID",
            provider_label="Idaho 511",
            base_url=settings.idaho_511_base_url,
            api_key=settings.idaho_511_api_key,
        ),
        Structured511CameraConnector(
            settings,
            source_name="alaska-511-cameras",
            owner="Alaska Department of Transportation and Public Facilities",
            state="AK",
            provider_label="Alaska 511",
            base_url=settings.alaska_511_base_url,
            api_key=settings.alaska_511_api_key,
        ),
        UsgsAshcamConnector(settings),
        WindyWebcamConnector(settings),
    ]


def _build_camera_entity(
    *,
    source: str,
    entity_id: str,
    label: str,
    latitude: float,
    longitude: float,
    fetched_at: str,
    external_url: str | None,
    camera_id: str | None,
    source_camera_id: str | None,
    owner: str | None,
    state: str | None,
    county: str | None,
    region: str | None,
    roadway: str | None,
    direction: str | None,
    location_description: str | None,
    feed_type: str,
    position: CameraPositionMetadata,
    orientation: CameraOrientationMetadata,
    frame: CameraFrameMetadata,
    compliance: CameraComplianceMetadata,
    metadata: dict[str, Any],
    reference_hint_text: str | None = None,
    facility_code_hint: str | None = None,
) -> CameraEntity:
    issues = _review_issues(position=position, orientation=orientation, frame=frame, compliance=compliance)
    confidence = min(
        1.0,
        ((position.confidence or 0.0) * 0.55)
        + ((orientation.confidence or 0.0) * 0.25)
        + (0.2 if frame.status in {"live", "viewer-page-only"} else 0.0),
    )
    quality_notes = list(position.notes) + list(orientation.notes)
    if frame.status == "viewer-page-only":
        quality_notes.append("Viewer fallback is available, but direct image retrieval is not confirmed.")
    if compliance.review_required:
        quality_notes.append("Compliance metadata requires manual review before broader operational use.")

    review_status: Literal["verified", "needs-review", "blocked"] = "verified"
    if frame.status == "blocked":
        review_status = "blocked"
    elif issues:
        review_status = "needs-review"

    health_state = "healthy"
    degraded_reason = None
    if frame.status == "blocked":
        health_state = "blocked"
        degraded_reason = "Frame access is blocked by authentication, terms, or upstream restrictions."
    elif frame.status in {"viewer-page-only", "unavailable"} or issues:
        health_state = "degraded"
        degraded_reason = issues[0].reason if issues else "Feed requires viewer fallback."

    return CameraEntity(
        id=entity_id,
        type="camera",
        source=source,
        label=label,
        latitude=latitude,
        longitude=longitude,
        altitude=0.0,
        heading=orientation.degrees if orientation.kind == "exact" else None,
        speed=None,
        timestamp=fetched_at,
        observed_at=frame.last_frame_at or fetched_at,
        fetched_at=fetched_at,
        status="active" if frame.status in {"live", "viewer-page-only", "stale"} else "degraded",
        source_detail=owner,
        external_url=external_url,
        confidence=confidence if confidence > 0 else None,
        history_available=False,
        canonical_ids={
            **({"cameraId": camera_id} if camera_id else {}),
            **({"sourceCameraId": source_camera_id} if source_camera_id else {}),
        },
        raw_identifiers={},
        quality=QualityMetadata(
            score=confidence if confidence > 0 else None,
            label=review_status,
            source_freshness_seconds=frame.age_seconds,
            notes=quality_notes,
        ),
        derived_fields=[
            DerivedField(
                name="coordinate_kind",
                value=position.kind,
                derived_from=position.source or "connector normalization",
                method="connector-normalization",
            ),
            DerivedField(
                name="orientation_kind",
                value=orientation.kind,
                derived_from=orientation.source or "connector normalization",
                method="connector-normalization",
            ),
        ],
        metadata=metadata,
        camera_id=camera_id,
        source_camera_id=source_camera_id,
        owner=owner,
        state=state,
        county=county,
        region=region,
        roadway=roadway,
        direction=direction,
        location_description=location_description,
        feed_type=feed_type,  # type: ignore[arg-type]
        access_policy="public-with-attribution",
        position=position,
        orientation=orientation,
        frame=frame,
        compliance=compliance,
        review=CameraReviewMetadata(
            status=review_status,
            reason=issues[0].reason if issues else None,
            required_actions=[issue.required_action for issue in issues],
            issue_categories=[issue.category for issue in issues],
        ),
        health_state=health_state,
        degraded_reason=degraded_reason,
        last_metadata_refresh_at=fetched_at,
        nearest_reference_ref_id=None,
        reference_link_status="unlinked",
        link_candidate_count=0,
        reference_hint_text=reference_hint_text or location_description,
        facility_code_hint=facility_code_hint,
    )


def _review_issues(
    *,
    position: CameraPositionMetadata,
    orientation: CameraOrientationMetadata,
    frame: CameraFrameMetadata,
    compliance: CameraComplianceMetadata,
) -> list[ConnectorIssue]:
    issues: list[ConnectorIssue] = []
    if position.kind != "exact":
        issues.append(
            ConnectorIssue(
                category="coordinate-verification",
                reason=f"Camera coordinates are {position.kind}, not exact.",
                required_action="Verify precise camera coordinates against authoritative source material.",
            )
        )
    if orientation.kind == "approximate":
        issues.append(
            ConnectorIssue(
                category="orientation-verification",
                reason="Camera orientation is cardinal-only or text-derived.",
                required_action="Confirm exact heading before presenting fixed directional precision.",
            )
        )
    elif orientation.kind == "unknown":
        issues.append(
            ConnectorIssue(
                category="orientation-verification",
                reason="Camera orientation is unknown.",
                required_action="Determine whether the camera has a fixed heading or should remain unknown.",
            )
        )
    elif orientation.kind == "ptz":
        issues.append(
            ConnectorIssue(
                category="ptz-classification",
                reason="Camera appears to be PTZ or dynamically oriented.",
                required_action="Verify PTZ/dynamic classification and suppress any fixed-heading presentation.",
            )
        )
    if frame.status == "viewer-page-only":
        issues.append(
            ConnectorIssue(
                category="viewer-fallback",
                reason="Camera currently has a viewer page fallback instead of a direct image URL.",
                required_action="Confirm whether a compliant direct image path exists or keep viewer-only handling.",
            )
        )
    if frame.status == "blocked":
        issues.append(
            ConnectorIssue(
                category="blocked",
                reason="Camera content is blocked by upstream restrictions.",
                required_action="Review upstream auth/terms restrictions before retrying ingestion.",
            )
        )
    if compliance.review_required:
        issues.append(
            ConnectorIssue(
                category="compliance-review",
                reason="Source/operator compliance requires manual review.",
                required_action="Confirm attribution, embed rights, and frame-storage rules before operational rollout.",
            )
        )
    return issues


def _classify_position(
    source_fields: list[Any],
    source_label: str,
) -> tuple[float | None, float | None, CameraPositionMetadata]:
    for field in source_fields:
        if not isinstance(field, dict):
            continue
        latitude = _first_float(field, "Latitude", "latitude")
        longitude = _first_float(field, "Longitude", "longitude")
        if latitude is not None and longitude is not None:
            return (
                latitude,
                longitude,
                CameraPositionMetadata(
                    kind="exact",
                    confidence=1.0,
                    source=source_label,
                    notes=[],
                ),
            )
    return (
        None,
        None,
        CameraPositionMetadata(
            kind="unknown",
            confidence=None,
            source=source_label,
            notes=["No trusted coordinates were available from the upstream payload."],
        ),
    )


def _classify_orientation(
    *,
    direction_text: str | None,
    degrees: float | None,
    source: str,
) -> CameraOrientationMetadata:
    if degrees is not None:
        return CameraOrientationMetadata(
            kind="exact",
            degrees=degrees % 360,
            cardinal_direction=direction_text,
            confidence=1.0,
            source=source,
            is_ptz=False,
            notes=[],
        )
    guess = _direction_to_orientation(direction_text)
    return CameraOrientationMetadata(
        kind=guess.kind,  # type: ignore[arg-type]
        degrees=guess.degrees,
        cardinal_direction=guess.cardinal_direction,
        confidence=guess.confidence,
        source=source,
        is_ptz=guess.is_ptz,
        notes=guess.notes,
    )


def _classify_frame(
    *,
    image_url: str | None,
    viewer_url: str | None,
    stream_url: str | None,
    width: int | None,
    height: int | None,
) -> CameraFrameMetadata:
    status: Literal["live", "stale", "unavailable", "viewer-page-only", "blocked"]
    if image_url:
        status = "live"
    elif viewer_url:
        status = "viewer-page-only"
    else:
        status = "unavailable"
    return CameraFrameMetadata(
        status=status,
        refresh_interval_seconds=60,
        last_frame_at=None,
        age_seconds=None,
        image_url=image_url,
        thumbnail_url=image_url,
        stream_url=stream_url,
        viewer_url=viewer_url,
        width=width,
        height=height,
    )


def _direction_to_orientation(direction: str | None) -> OrientationGuess:
    if not direction:
        return OrientationGuess(
            kind="unknown",
            degrees=None,
            cardinal_direction=None,
            confidence=None,
            is_ptz=False,
            notes=["No orientation field was provided by the source."],
        )
    normalized = direction.strip().lower()
    if normalized == "ptz":
        return OrientationGuess(
            kind="ptz",
            degrees=None,
            cardinal_direction="PTZ",
            confidence=1.0,
            is_ptz=True,
            notes=["PTZ camera orientation changes over time and is not treated as fixed."],
        )
    mapping = {
        "northbound": 0.0,
        "eastbound": 90.0,
        "southbound": 180.0,
        "westbound": 270.0,
        "inbound": None,
        "outbound": None,
        "both directions": None,
        "all directions": None,
        "none": None,
    }
    if normalized in mapping:
        return OrientationGuess(
            kind="approximate",
            degrees=mapping[normalized],
            cardinal_direction=direction,
            confidence=0.65 if mapping[normalized] is not None else 0.35,
            is_ptz=False,
            notes=["Orientation inferred from cardinal direction text rather than surveyed heading."],
        )
    return OrientationGuess(
        kind="unknown",
        degrees=None,
        cardinal_direction=direction,
        confidence=0.2,
        is_ptz=False,
        notes=["Orientation text could not be translated into a trustworthy fixed heading."],
    )


def _safe_json(response: httpx.Response) -> Any:
    response.raise_for_status()
    return response.json()


def _redirect_link(raw_links: Any) -> str | None:
    if not isinstance(raw_links, list):
        return None
    for entry in raw_links:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("Rel", "")).lower() == "redirect":
            href = entry.get("Href")
            if isinstance(href, str):
                return href
    return None


def _windy_image_url(images: Any) -> str | None:
    if not isinstance(images, dict):
        return None
    current = images.get("current")
    if isinstance(current, dict):
        for key in ("preview", "icon", "thumbnail"):
            value = current.get(key)
            if isinstance(value, str):
                return value
        sizes = current.get("sizes")
        if isinstance(sizes, dict):
            for key in ("preview", "thumbnail", "icon"):
                nested = sizes.get(key)
                if isinstance(nested, dict) and isinstance(nested.get("link"), str):
                    return nested["link"]
    return None


def _bookmark_code(url: str | None) -> str | None:
    if not url or "bookmark=" not in url:
        return None
    return url.split("bookmark=", 1)[1].split("&", 1)[0] or None


def _extract_windy_webcams(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        result = payload.get("result")
        if isinstance(result, dict) and isinstance(result.get("webcams"), list):
            return [item for item in result["webcams"] if isinstance(item, dict)]
        webcams = payload.get("webcams")
        if isinstance(webcams, list):
            return [item for item in webcams if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def _first_nested_str(value: Any, *paths: tuple[str, str]) -> str | None:
    if not isinstance(value, dict):
        return None
    for path in paths:
        current: Any = value
        for key in path:
            if not isinstance(current, dict):
                current = None
                break
            current = current.get(key)
        if isinstance(current, str) and current.strip():
            return current.strip()
    return None


def _first_str(item: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str):
            text = value.strip()
            if text:
                return text
    return None


def _first_float(item: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = item.get(key)
        if value is None or isinstance(value, bool):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _first_int(item: dict[str, Any], *keys: str) -> int | None:
    for key in keys:
        value = item.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str) and value.strip():
            try:
                return int(float(value))
            except ValueError:
                continue
    return None


def _hash_label(value: str) -> str:
    return sha1(value.encode("utf-8")).hexdigest()[:12]


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
