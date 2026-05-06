# Features/Webcam AI Phase 2 To Phase 3 Handoff

## Scope completed

- Built and stabilized the webcam/source-operations backend evidence stack for candidate lifecycle work.
- Added read-only candidate endpoint reports, graduation plans, sandbox validation reporting, source-ops detail/index/export surfaces, review queues, and aggregate export helpers.
- Added bounded cohort-level artifacts on top of the same evidence path:
  - `cameraSandboxReadinessComparisonReport`
  - `cameraSourceOpsPortfolioDigest`
  - `cameraSourceOpsReviewPriorityPacket`
  - `cameraSourceOpsRegionalPortfolioPacket`
  - `cameraSourceOpsOsmLeadDiscoveryPacket`
  - `cameraSourceOpsOsmLeadReviewReconciliationPacket`
- Added fixture-first sandbox connectors for the strongest candidate cohort already cleared for conservative mapping proof:
  - `finland-digitraffic-road-cameras`
  - `nsw-live-traffic-cameras`
  - `quebec-mtmd-traffic-cameras`
  - `maryland-chart-traffic-cameras`
  - `fingal-traffic-cameras`
  - `baton-rouge-traffic-cameras`
  - `vancouver-web-cam-url-links`
  - `caltrans-cctv-cameras`
- Added endpoint-verified non-sandbox holds where endpoint evidence is real but still weaker than the sandbox cohort:
  - `nzta-traffic-cameras`
  - `arlington-traffic-cameras`
- Preserved blocked/review-gated candidates without unsafe promotion:
  - `minnesota-511-public-arcgis`
  - `euskadi-traffic-cameras`
  - `wsdot-cameras` as credential-blocked

## Current state

- `usgs-ashcam` is the only validated/active source in this lane.
- All newer cohort additions remain candidate-only or endpoint-verified-only.
- Sandbox-importable does not mean approved, active, or validated.
- Endpoint-verified does not mean sandbox-ready, ingest-ready, or direct-image-proven.
- OSM-backed artifacts are lead-discovery and review-posture aids only.
- Map-only leads remain below endpoint proof and below activation readiness.
- The current webcam/source-ops checkpoint is coherent and complete enough to hand off without opening another candidate-harvest wave.

Candidate posture snapshot:

- Direct-image-documented plus sandbox-importable:
  - `finland-digitraffic-road-cameras`
  - `nsw-live-traffic-cameras`
  - `caltrans-cctv-cameras`
- Viewer-only-documented plus sandbox-importable:
  - `quebec-mtmd-traffic-cameras`
  - `maryland-chart-traffic-cameras`
  - `baton-rouge-traffic-cameras`
  - `vancouver-web-cam-url-links`
- Metadata-only-documented plus sandbox-importable:
  - `fingal-traffic-cameras`
- Endpoint-verified but held:
  - `nzta-traffic-cameras`
  - `arlington-traffic-cameras`
- Needs-review or blocked:
  - `euskadi-traffic-cameras`
  - `minnesota-511-public-arcgis`
  - `wsdot-cameras` credential-blocked

## Files and surfaces to know

Core registry and lifecycle posture:

- [`app/server/src/services/camera_registry.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_registry.py)
- [`app/server/src/services/camera_candidate_endpoint_report.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_candidate_endpoint_report.py)
- [`app/server/src/services/camera_candidate_graduation_plan.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_candidate_graduation_plan.py)
- [`app/server/src/services/camera_sandbox_validation_report.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_sandbox_validation_report.py)

Source-ops summary and reporting surfaces:

- [`app/server/src/services/camera_source_ops_detail.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_source_ops_detail.py)
- [`app/server/src/services/camera_source_ops_report_index.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_source_ops_report_index.py)
- [`app/server/src/services/camera_source_ops_export_summary.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_source_ops_export_summary.py)
- [`app/server/src/services/camera_source_ops_review_queue.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_source_ops_review_queue.py)
- [`app/server/src/services/camera_source_ops_evidence_packets.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_source_ops_evidence_packets.py)
- [`app/server/src/services/camera_source_ops_export_readiness.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_source_ops_export_readiness.py)

Cohort-level evidence artifacts:

- [`app/server/src/services/camera_source_ops_candidate_network_summary.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_source_ops_candidate_network_summary.py)
- [`app/server/src/services/camera_source_ops_promotion_readiness_summary.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_source_ops_promotion_readiness_summary.py)
- [`app/server/src/services/camera_source_ops_sandbox_readiness_comparison.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_source_ops_sandbox_readiness_comparison.py)
- [`app/server/src/services/camera_source_ops_portfolio_digest.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_source_ops_portfolio_digest.py)
- [`app/server/src/services/camera_source_ops_review_priority_packet.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_source_ops_review_priority_packet.py)
- [`app/server/src/services/camera_source_ops_regional_portfolio_packet.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_source_ops_regional_portfolio_packet.py)
- [`app/server/src/services/camera_source_ops_osm_lead_discovery_packet.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_source_ops_osm_lead_discovery_packet.py)
- [`app/server/src/services/camera_source_ops_osm_lead_review_reconciliation_packet.py`](/C:/Users/mike/11Writer/app/server/src/services/camera_source_ops_osm_lead_review_reconciliation_packet.py)

API contracts and route surface:

- [`app/server/src/types/api.py`](/C:/Users/mike/11Writer/app/server/src/types/api.py)
- [`app/server/src/routes/cameras.py`](/C:/Users/mike/11Writer/app/server/src/routes/cameras.py)

Candidate connectors and fixtures:

- [`app/server/src/adapters/cameras.py`](/C:/Users/mike/11Writer/app/server/src/adapters/cameras.py)
- [`app/server/data/finland_digitraffic_weathercam_fixture.json`](/C:/Users/mike/11Writer/app/server/data/finland_digitraffic_weathercam_fixture.json)
- [`app/server/data/nsw_live_traffic_cameras_fixture.json`](/C:/Users/mike/11Writer/app/server/data/nsw_live_traffic_cameras_fixture.json)
- [`app/server/data/quebec_mtmd_traffic_cameras_fixture.json`](/C:/Users/mike/11Writer/app/server/data/quebec_mtmd_traffic_cameras_fixture.json)
- [`app/server/data/maryland_chart_traffic_cameras_fixture.json`](/C:/Users/mike/11Writer/app/server/data/maryland_chart_traffic_cameras_fixture.json)
- [`app/server/data/fingal_traffic_cameras_fixture.json`](/C:/Users/mike/11Writer/app/server/data/fingal_traffic_cameras_fixture.json)
- [`app/server/data/baton_rouge_traffic_cameras_fixture.json`](/C:/Users/mike/11Writer/app/server/data/baton_rouge_traffic_cameras_fixture.json)
- [`app/server/data/vancouver_web_cam_url_links_fixture.json`](/C:/Users/mike/11Writer/app/server/data/vancouver_web_cam_url_links_fixture.json)
- [`app/server/data/caltrans_cctv_cameras_fixture.json`](/C:/Users/mike/11Writer/app/server/data/caltrans_cctv_cameras_fixture.json)

Docs that carry the lane truth:

- [`app/docs/webcams.md`](/C:/Users/mike/11Writer/app/docs/webcams.md)
- [`app/docs/webcam-source-lifecycle-policy.md`](/C:/Users/mike/11Writer/app/docs/webcam-source-lifecycle-policy.md)
- [`app/docs/webcam-global-camera-candidate-batch-2026-05.md`](/C:/Users/mike/11Writer/app/docs/webcam-global-camera-candidate-batch-2026-05.md)
- [`app/docs/agent-progress/features-webcam-ai.md`](/C:/Users/mike/11Writer/app/docs/agent-progress/features-webcam-ai.md)

## Validation already run

Most recent full backend validation set for the active checkpoint:

- `python -m pytest app/server/tests/test_webcam_module.py -q`
- `python -m pytest app/server/tests/test_camera_candidate_endpoint_report.py app/server/tests/test_camera_candidate_graduation_plan.py -q`
- `python -m pytest app/server/tests/test_camera_source_ops_report_index.py app/server/tests/test_camera_source_ops_detail.py app/server/tests/test_camera_source_ops_export_summary.py -q`
- `python -m pytest app/server/tests/test_camera_sandbox_validation_report.py -q`
- `python -m compileall app/server/src`
- `python scripts/alerts_ledger.py --json`

Focused tests were also run during each artifact step for:

- report index
- export summary
- OSM lead-discovery packet
- OSM lead-to-review reconciliation packet

## Known blockers or caveats

- Candidate does not equal validated.
- Sandbox-importable does not equal approved-unvalidated.
- Endpoint-verified does not equal media-proof-complete.
- OSM map presence does not equal a public live camera endpoint.
- Viewer-only and metadata-only sources must stay below direct-image proof.
- The current official backlog still does not justify another clean candidate promotion wave under the bar already encoded in the lane.

Specific backlog cautions:

- `qldtraffic-web-cameras`
  - still not pinned cleanly enough at payload/media level
- `seattle-traffic-cameras`
  - still viewer-page centric
- `npra-datex-webcams`
  - still registration-gated

Compliance and provenance cautions:

- preserve attribution and terms posture from source registry compliance metadata
- do not infer frame-storage rights from endpoint reachability
- do not collapse blocked and credential-blocked into the same operational meaning
- do not infer direct-image rights from viewer-link presence

UI and surface caveats:

- source-ops surfaces are operational and interim
- they are not final public UX truth
- they are evidence and workflow support for operators, Reporting AI, and future Phase 3 integration work

## What the next AI should do first

For Workspace AI:

- read [`app/docs/webcams.md`](/C:/Users/mike/11Writer/app/docs/webcams.md) and [`app/docs/webcam-source-lifecycle-policy.md`](/C:/Users/mike/11Writer/app/docs/webcam-source-lifecycle-policy.md) first
- then inspect [`app/server/src/types/api.py`](/C:/Users/mike/11Writer/app/server/src/types/api.py) and the report/export services before changing route or contract shapes

For Reporting AI:

- treat the source-ops packets as export-safe operational evidence only
- reuse the existing packet hierarchy instead of inventing new lifecycle semantics
- keep candidate/sandbox/endpoint-only/blocked distinctions intact

For Platform AI:

- do not enable ingestion from any of the candidate connectors by default
- do not widen live-mode or scheduled refresh paths without explicit lifecycle review
- preserve fixture-first defaults for sandbox connectors

For Connect AI:

- if any future frontend or shared-contract work consumes these packets, preserve the explicit caveat and does-not-prove lines
- do not compress operational distinctions away during UI cleanup

## What not to break

- Do not break `usgs-ashcam` validated posture.
- Do not promote any candidate to validated from endpoint, fixture, sandbox, OSM, or export evidence alone.
- Do not flip sandbox connectors into live-default ingest.
- Do not remove or weaken:
  - `does_not_prove_lines`
  - provenance fields
  - blocked versus credential-blocked separation
  - direct-image versus viewer-only versus metadata-only separation
  - endpoint-known versus map-only separation
- Do not leak:
  - candidate endpoint URLs into compact export lines where they were intentionally omitted
  - credentials, tokens, local paths, or unsafe operational detail into export-safe packets
- Do not let Phase 3 UI cleanup normalize away review burden, missing evidence, or next safe review step.

## Phase 3 relevance

- This lane is ready for Phase 3 consumers that need operational camera-source evidence, not live ingest expansion.
- The strongest Phase 3 value is coordination and reporting:
  - candidate lifecycle reporting
  - source-ops export composition
  - operator-facing review posture
  - conservative candidate comparison
  - careful UI consumption of existing backend evidence

Most useful Phase 3 truths:

- validated is still rare and explicit
- sandbox-importable is only mapping/readiness evidence
- endpoint-known is still weaker than validated
- viewer-only and metadata-only remain materially weaker than direct-image-documented
- OSM/Overpass/Geofabrik support is helpful for lead discovery and reconciliation, but it must stay below endpoint proof and activation authority

Phase 3 should treat this lane as a mature evidence/reporting substrate with strict safety semantics, not as permission to open a new aggressive candidate-harvesting or activation wave.
