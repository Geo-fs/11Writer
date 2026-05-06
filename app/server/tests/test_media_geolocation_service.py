from __future__ import annotations

import json
from pathlib import Path

from src.config.settings import Settings
from src.services import media_evidence_service


def test_geoclip_candidates_use_offline_place_enrichment(tmp_path: Path, monkeypatch) -> None:
    gazetteer_path = tmp_path / "gazetteer.json"
    gazetteer_path.write_text(
        json.dumps(
            {
                "places": [
                    {
                        "name": "Golden Gate Bridge",
                        "kind": "landmark",
                        "latitude": 37.8199,
                        "longitude": -122.4783,
                        "locality": "San Francisco",
                        "admin1": "California",
                        "country": "United States",
                        "countryCode": "US",
                    },
                    {
                        "name": "San Francisco",
                        "kind": "city",
                        "latitude": 37.7749,
                        "longitude": -122.4194,
                        "admin1": "California",
                        "country": "United States",
                        "countryCode": "US",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    artifact_path = tmp_path / "artifact.jpg"
    artifact_path.write_bytes(b"fixture")
    settings = Settings(
        APP_ENV="test",
        SOURCE_DISCOVERY_DATABASE_URL=f"sqlite:///{(tmp_path / 'source_discovery.db').as_posix()}",
        WAVE_MONITOR_DATABASE_URL=f"sqlite:///{(tmp_path / 'wave_monitor.db').as_posix()}",
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_ENABLED=True,
        SOURCE_DISCOVERY_MEDIA_GEOLOCATION_PLACE_GAZETTEER_PATH=str(gazetteer_path),
    )

    class _FakeGeoClipModel:
        def predict(self, artifact_path: str, top_k: int):
            del artifact_path, top_k
            return [[37.8199, -122.4783]], [0.93]

    def _fake_load_runtime(settings: Settings):
        del settings
        return (
            {"model": _FakeGeoClipModel(), "model_name": "fake-geoclip"},
            media_evidence_service.MediaGeolocationEngineAttempt(
                engine="geoclip",
                role="specialized_geocoder",
                status="available",
                model_name="fake-geoclip",
                warm_state="warm",
            ),
        )

    monkeypatch.setattr(media_evidence_service, "_load_geoclip_runtime", _fake_load_runtime)

    candidates, model_name, reasoning, caveats, attempt = media_evidence_service._try_geoclip_candidates(
        settings,
        artifact_path=str(artifact_path),
        max_candidates=1,
    )

    assert model_name == "fake-geoclip"
    assert attempt.status == "completed"
    assert attempt.metadata["usedPlaceEnrichment"] is True
    assert candidates[0].label == "Golden Gate Bridge, San Francisco, California, United States"
    assert candidates[0].metadata["locality"] == "San Francisco"
    assert candidates[0].metadata["country"] == "United States"
    assert "offline_place_gazetteer" in candidates[0].provenance_chain
    assert any("offline place labels" in line for line in reasoning)
    assert caveats


def test_geolocation_candidate_agreement_uses_enriched_place_context() -> None:
    geoclip_candidate = media_evidence_service.MediaGeolocationCandidate(
        rank=1,
        candidate_kind="gps_point",
        label="Golden Gate Bridge, San Francisco, California, United States",
        latitude=37.8199,
        longitude=-122.4783,
        confidence=0.93,
        engine="geoclip",
        metadata={
            "landmark": "Golden Gate Bridge",
            "locality": "San Francisco",
            "admin1": "California",
            "country": "United States",
            "agreementLabels": ["Golden Gate Bridge", "San Francisco", "California", "United States"],
        },
    )
    streetclip_candidate = media_evidence_service.MediaGeolocationCandidate(
        rank=1,
        candidate_kind="country_region",
        label="San Francisco",
        latitude=None,
        longitude=None,
        confidence=0.74,
        engine="streetclip",
    )

    assert media_evidence_service._geolocation_candidates_agree(geoclip_candidate, streetclip_candidate) is True
    assert media_evidence_service._geolocation_candidates_conflict(geoclip_candidate, streetclip_candidate) is False


def test_geoclip_candidates_reuse_prediction_cache_and_emit_profile_metadata(
    tmp_path: Path,
    monkeypatch,
) -> None:
    media_evidence_service._GEOCLIP_PREDICTION_CACHE.clear()
    artifact_path = tmp_path / "artifact.jpg"
    artifact_path.write_bytes(b"fixture")
    settings = Settings(
        APP_ENV="test",
        SOURCE_DISCOVERY_DATABASE_URL=f"sqlite:///{(tmp_path / 'source_discovery.db').as_posix()}",
        WAVE_MONITOR_DATABASE_URL=f"sqlite:///{(tmp_path / 'wave_monitor.db').as_posix()}",
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_ENABLED=True,
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_RUNTIME_PROFILE="balanced",
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_TARGET_DEVICE="cpu",
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_PREDICTION_CACHE_ENTRIES=8,
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_MAX_IMAGE_EDGE=1024,
    )

    class _FakeGeoClipModel:
        def __init__(self) -> None:
            self.predict_calls = 0

        def predict(self, artifact_path: str, top_k: int):
            del artifact_path, top_k
            self.predict_calls += 1
            return [[35.0, 139.0]], [0.87]

    fake_model = _FakeGeoClipModel()

    def _fake_load_runtime(settings: Settings):
        del settings
        return (
            {
                "model": fake_model,
                "model_name": "fake-geoclip",
                "cache_key": "runtime:test",
                "performance_profile": "balanced",
                "max_image_edge": 1024,
                "requested_device": "cpu",
                "resolved_device": "cpu",
                "prediction_cache_entries": 8,
                "experimental_acceleration_enabled": False,
            },
            media_evidence_service.MediaGeolocationEngineAttempt(
                engine="geoclip",
                role="specialized_geocoder",
                status="available",
                model_name="fake-geoclip",
                warm_state="warm",
                metadata={
                    "performanceProfile": "balanced",
                    "requestedDevice": "cpu",
                    "resolvedDevice": "cpu",
                    "predictionCacheEntries": 8,
                },
            ),
        )

    monkeypatch.setattr(media_evidence_service, "_load_geoclip_runtime", _fake_load_runtime)
    monkeypatch.setattr(
        media_evidence_service,
        "_prepare_geoclip_inference_artifact",
        lambda *args, **kwargs: (
            str(artifact_path),
            {
                "profile": "balanced",
                "requestedDevice": "cpu",
                "resolvedDevice": "cpu",
                "maxImageEdge": 1024,
                "usedPreprocessedArtifact": True,
                "sourceWidth": 4000,
                "sourceHeight": 3000,
                "inferenceWidth": 1024,
                "inferenceHeight": 768,
                "preprocessedArtifactPath": str(artifact_path),
            },
            ["GeoCLIP inference used the explicit `balanced` profile with max image edge 1024px to reduce runtime cost."],
        ),
    )

    first_candidates, _, first_reasoning, _, first_attempt = media_evidence_service._try_geoclip_candidates(
        settings,
        artifact_path=str(artifact_path),
        max_candidates=1,
    )
    second_candidates, _, second_reasoning, _, second_attempt = media_evidence_service._try_geoclip_candidates(
        settings,
        artifact_path=str(artifact_path),
        max_candidates=1,
    )

    assert fake_model.predict_calls == 1
    assert first_candidates[0].latitude == 35.0
    assert second_candidates[0].longitude == 139.0
    assert first_attempt.metadata["performanceProfile"] == "balanced"
    assert first_attempt.metadata["usedPreprocessedArtifact"] is True
    assert first_attempt.metadata["cacheHit"] is False
    assert second_attempt.metadata["cacheHit"] is True
    assert second_attempt.metadata["requestedDevice"] == "cpu"
    assert any("cached prediction" in line.casefold() for line in second_reasoning)
    assert any("preprocessed artifact" in line.casefold() for line in first_reasoning)


def test_deterministic_geolocation_clue_packet_extracts_route_operator_and_gazetteer_clues(
    tmp_path: Path,
) -> None:
    gazetteer_path = tmp_path / "gazetteer.json"
    gazetteer_path.write_text(
        json.dumps(
            {
                "places": [
                    {
                        "name": "Bixby Creek Bridge",
                        "kind": "landmark",
                        "aliases": ["Bixby Bridge"],
                        "latitude": 36.3725,
                        "longitude": -121.9025,
                        "locality": "Big Sur",
                        "admin1": "California",
                        "country": "United States",
                        "countryCode": "US",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    settings = Settings(
        APP_ENV="test",
        SOURCE_DISCOVERY_DATABASE_URL=f"sqlite:///{(tmp_path / 'source_discovery.db').as_posix()}",
        WAVE_MONITOR_DATABASE_URL=f"sqlite:///{(tmp_path / 'wave_monitor.db').as_posix()}",
        SOURCE_DISCOVERY_MEDIA_GEOLOCATION_PLACE_GAZETTEER_PATH=str(gazetteer_path),
    )

    clue_packet, reasoning_lines, _ = media_evidence_service._extract_geolocation_clue_packet(
        settings=settings,
        observed_latitude=None,
        observed_longitude=None,
        exif_timestamp="2026-05-05T18:45:00Z",
        ocr_text="\n".join(
            [
                "Bixby Creek Bridge overlook",
                "US-101 Scenic Highway",
                "Keep right",
                "Caltrain rider notice",
                "36.3725 N 121.9025 W",
            ]
        ),
        captions=["Coastal bridge viewpoint in California"],
        artifact_metadata={
            "seasonalSignals": {"greenRatio": 0.34, "blueRatio": 0.37},
            "daylightSignals": {"brightness": 0.49, "dominantBrightSide": "left"},
        },
        prior_place_hypothesis=None,
        prior_place_confidence=None,
        prior_place_basis=None,
        prior_geolocation_hypothesis=None,
        prior_geolocation_confidence=None,
        prior_geolocation_basis=None,
        inherited_context=None,
    )

    assert any(clue.clue_type == "cardinal_coordinates" and clue.latitude == 36.3725 and clue.longitude == -121.9025 for clue in clue_packet.coordinate_clues)
    assert any(clue.clue_type == "gazetteer_landmark" and clue.text == "Bixby Creek Bridge" for clue in clue_packet.place_text_clues)
    assert any(clue.clue_type == "us_route" and clue.text == "US 101" for clue in clue_packet.place_text_clues)
    assert any(clue.clue_type == "driving_side_text" and clue.normalized_value == "right_driving" for clue in clue_packet.place_text_clues)
    assert any(clue.clue_type == "transit_operator" and clue.text == "Caltrain" for clue in clue_packet.place_text_clues)
    assert any(clue.clue_type == "coastal_context" for clue in clue_packet.environment_clues)
    assert any(clue.clue_type == "time_of_day_guess" and clue.text == "daylight" for clue in clue_packet.time_clues)
    assert any("deterministic geolocation builds structured clues" in line.casefold() for line in reasoning_lines)


def test_media_geolocation_model_health_inspection_reports_local_asset_readiness(
    tmp_path: Path,
    monkeypatch,
) -> None:
    geoclip_weights_dir = tmp_path / "geoclip-weights"
    geoclip_weights_dir.mkdir()
    for file_name in ["image_encoder_mlp_weights.pth", "location_encoder_weights.pth", "logit_scale_weights.pth"]:
        (geoclip_weights_dir / file_name).write_bytes(b"ok")

    geoclip_clip_dir = tmp_path / "geoclip-clip"
    geoclip_clip_dir.mkdir()
    (geoclip_clip_dir / "config.json").write_text("{}", encoding="utf-8")
    (geoclip_clip_dir / "model.safetensors").write_bytes(b"weights")

    streetclip_dir = tmp_path / "streetclip"
    streetclip_dir.mkdir()
    (streetclip_dir / "config.json").write_text("{}", encoding="utf-8")
    (streetclip_dir / "model.bin").write_bytes(b"weights")

    settings = Settings(
        APP_ENV="test",
        SOURCE_DISCOVERY_DATABASE_URL=f"sqlite:///{(tmp_path / 'source_discovery.db').as_posix()}",
        WAVE_MONITOR_DATABASE_URL=f"sqlite:///{(tmp_path / 'wave_monitor.db').as_posix()}",
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_ENABLED=True,
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_EXPECTED_VERSION="1.0.0",
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_WEIGHTS_PATH=str(geoclip_weights_dir),
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_CLIP_BACKBONE_DIR=str(geoclip_clip_dir),
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_RUNTIME_PROFILE="balanced",
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_TARGET_DEVICE="cpu",
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_MAX_IMAGE_EDGE=1536,
        SOURCE_DISCOVERY_MEDIA_STREETCLIP_ENABLED=True,
        SOURCE_DISCOVERY_MEDIA_STREETCLIP_EXPECTED_TRANSFORMERS_VERSION="5.0.0",
        SOURCE_DISCOVERY_MEDIA_STREETCLIP_LOCAL_DIR=str(streetclip_dir),
    )

    monkeypatch.setattr(media_evidence_service, "GeoCLIP", object())
    monkeypatch.setattr(media_evidence_service, "Image", object())
    monkeypatch.setattr(media_evidence_service, "torch", object())
    monkeypatch.setattr(media_evidence_service, "AutoModel", object())
    monkeypatch.setattr(media_evidence_service, "AutoProcessor", object())
    monkeypatch.setattr(
        media_evidence_service,
        "_installed_distribution_version",
        lambda distribution_name: {"geoclip": "1.0.0", "transformers": "5.0.0"}.get(distribution_name),
    )
    monkeypatch.setattr(
        media_evidence_service,
        "_geoclip_runtime_state",
        lambda *args, **kwargs: (False, "cold", None),
    )
    monkeypatch.setattr(
        media_evidence_service,
        "_streetclip_runtime_state",
        lambda *args, **kwargs: (True, "warm", "2026-05-05T23:59:00Z"),
    )

    geoclip_health = media_evidence_service.inspect_media_geolocation_model(settings, "geoclip")
    streetclip_health = media_evidence_service.inspect_media_geolocation_model(settings, "streetclip")

    assert geoclip_health.install_ready is True
    assert geoclip_health.runtime_ready is False
    assert geoclip_health.status == "ready"
    assert "weights" in geoclip_health.present_components
    assert "clip_backbone_snapshot" in geoclip_health.present_components
    assert geoclip_health.metadata["performanceProfile"] == "balanced"
    assert geoclip_health.metadata["resolvedDevice"] == "cpu"
    assert geoclip_health.metadata["maxImageEdge"] == 1536
    assert streetclip_health.install_ready is True
    assert streetclip_health.runtime_ready is True
    assert streetclip_health.warm_state == "warm"
    assert streetclip_health.status == "ready"


def test_media_geolocation_model_health_fails_closed_for_unapproved_non_cpu_device(
    tmp_path: Path,
    monkeypatch,
) -> None:
    geoclip_weights_dir = tmp_path / "geoclip-weights"
    geoclip_weights_dir.mkdir()
    for file_name in ["image_encoder_mlp_weights.pth", "location_encoder_weights.pth", "logit_scale_weights.pth"]:
        (geoclip_weights_dir / file_name).write_bytes(b"ok")

    geoclip_clip_dir = tmp_path / "geoclip-clip"
    geoclip_clip_dir.mkdir()
    (geoclip_clip_dir / "config.json").write_text("{}", encoding="utf-8")
    (geoclip_clip_dir / "model.safetensors").write_bytes(b"weights")

    settings = Settings(
        APP_ENV="test",
        SOURCE_DISCOVERY_DATABASE_URL=f"sqlite:///{(tmp_path / 'source_discovery.db').as_posix()}",
        WAVE_MONITOR_DATABASE_URL=f"sqlite:///{(tmp_path / 'wave_monitor.db').as_posix()}",
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_ENABLED=True,
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_EXPECTED_VERSION="1.0.0",
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_WEIGHTS_PATH=str(geoclip_weights_dir),
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_CLIP_BACKBONE_DIR=str(geoclip_clip_dir),
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_TARGET_DEVICE="cuda",
        SOURCE_DISCOVERY_MEDIA_GEOCLIP_ALLOW_EXPERIMENTAL_ACCELERATION=False,
    )

    monkeypatch.setattr(media_evidence_service, "GeoCLIP", object())
    monkeypatch.setattr(
        media_evidence_service,
        "_installed_distribution_version",
        lambda distribution_name: "1.0.0" if distribution_name == "geoclip" else None,
    )

    health = media_evidence_service.inspect_media_geolocation_model(settings, "geoclip")

    assert health.status == "unsupported_runtime"
    assert health.install_ready is False
    assert "Non-CPU GeoCLIP execution is gated" in (health.summary or "")
