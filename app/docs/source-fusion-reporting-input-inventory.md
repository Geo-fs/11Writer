# Source Fusion / Reporting Input Inventory

## Purpose

This doc is a current-state inventory for the emerging evidence-aware reporting desk direction in 11Writer.

It is meant to answer three questions quickly:

1. Which domain surfaces already produce bounded fusion/reporting inputs?
2. Which files are still user-facing panels or high-collision shared integration surfaces?
3. Which runtime slices remain review-only or runtime-boundary only and should not be overclaimed as analyst-proof reporting features?

Use this with:

- `app/docs/active-agent-worktree.md`
- `app/docs/release-readiness.md`
- `app/docs/validation-matrix.md`
- `app/docs/commit-groups.current.md`
- `app/docs/source-onboarding-contract.md`

## Shared source-onboarding contract

Neutral onboarding/governance contract:

- `app/docs/source-onboarding-contract.md`

Current role:

- ties together shared rules for:
  - auth posture
  - machine-usability posture
  - fixture-first expectations
  - source mode, source health, freshness, and evidence basis expectations
  - polite-header, request-budget, cache, and export-safe posture
  - prompt-injection-safe handling for feed, bulletin, article, and OCR text

Guardrail truth:

- this contract supports source expansion and reporting-input honesty
- it does not promote browser-only, discovery-only, or runtime-only surfaces into implementation proof
- it does not override lane ownership or source-validation status

## Stable fusion / reporting inputs

These surfaces are currently implemented enough to treat as real bounded reporting inputs rather than placeholder planning.

### Aerospace

- Input builders:
  - `app/client/src/features/inspector/aerospaceCurrentAwarenessDigest.ts`
  - `app/client/src/features/inspector/aerospaceReportingHandoffContract.ts`
  - `app/client/src/features/inspector/aerospaceFusionSnapshotInput.ts`
  - `app/client/src/features/inspector/aerospaceReportBriefPackage.ts`
  - `app/client/src/features/inspector/aerospaceVaacAdvisoryReportPackage.ts`
  - `app/client/src/features/inspector/aerospaceEvidenceTimelinePackage.ts`
  - `app/client/src/features/inspector/aerospacePackageCoherence.ts`
  - `app/client/src/features/inspector/aerospaceWorkflowValidationEvidenceSnapshot.ts`
- Current role:
  - current-awareness digest for export-safe aerospace awareness context
  - reporting handoff contract for export/reporting lineage across packet, brief, digest, continuity, advisory, and workflow-validation surfaces
  - bounded metadata/accounting packages
  - evidence timeline, validation posture, export/readiness, review/export bundle coherence
  - selected-target-aware fusion snapshot input for future reporting-desk composition
  - report-brief packaging over the existing fusion snapshot input
  - VAAC advisory report packaging as an adjacent report-support surface that preserves advisory/source-health lineage without pretending to be a full cross-context brief
- Guardrail truth:
  - these inputs preserve source health, evidence basis, caveats, and does-not-prove lines
  - they do not prove intent, route consequence, failure, threat, or action recommendation

### Data AI

- Input builders:
  - `app/client/src/features/inspector/dataAiSourceIntelligence.ts`
- Current role:
  - family/source readiness summaries
  - fusion snapshot summary
  - report-brief package
  - current-awareness digest
  - topic-safe report export packet
  - question briefing packet
  - infrastructure/status context
  - topic lens
  - long-tail discovery posture
- Guardrail truth:
  - workflow-supporting evidence only
  - metadata-only grouping and readiness/review posture
  - no truth, severity, threat, attribution, legal, remediation, or action scoring

### Marine

- Input builders and aggregators:
  - `app/client/src/features/marine/marineEvidenceSummary.ts`
  - `app/client/src/features/marine/marineFusionSnapshotInput.ts`
  - `app/client/src/features/marine/marineCurrentAwarenessDigest.ts`
  - supporting bounded packages already consumed there, including context fusion, context review/report, issue export bundle, corridor review, and source-health export coherence
- Current role:
  - anomaly attention plus environmental/hydrology/context export-safe summaries
  - fusion snapshot input for later reporting composition
  - current-awareness digest for export-safe marine awareness context
  - corridor and chokepoint review/accounting packages
  - source-health workflow and report surfaces that can feed later reporting-desk composition
- Guardrail truth:
  - review and export support only
  - no intent, wrongdoing, or action-proof laundering

### Geospatial / Base Earth reference context

- Backend input routes/services:
  - `app/server/src/routes/base_earth_context.py`
  - `app/server/src/routes/environmental_context.py`
  - `app/server/src/services/geoboundaries_admin_service.py`
  - `app/server/src/services/meteoalarm_atom_service.py`
  - `app/server/src/services/dwd_cap_alerts_service.py`
  - `app/server/src/services/rgi_glacier_inventory_service.py`
  - related natural-earth, GSHHG, PB2002, and NOAA global volcano reference services
- Shared contracts:
  - `app/server/src/types/api.py`
  - `app/client/src/types/api.ts`
- Current role:
  - bounded environmental current-awareness digest support and export-safe overview
  - bounded reference/export package and review queue for base-earth context
  - bounded environmental fusion-snapshot input over dynamic environmental, Canada, base-earth, glacier, and DWD CAP warning surfaces
  - static/reference contextual layers that can enrich reporting without pretending to be live hazard truth
- Guardrail truth:
  - reference or contextual only
  - `geoboundaries-admin` is static/admin boundary context only
  - `meteoalarm-atom` is bounded advisory/contextual warning-distribution context only
  - not current hazard truth, melt-rate truth, glacier-change proof, or action guidance

## User-facing panels and shared integration surfaces

These files currently compose multiple domain inputs and remain manual-review territory.

- `app/client/src/features/app-shell/AppShell.tsx`
- `app/client/src/features/inspector/InspectorPanel.tsx`
- `app/client/src/features/layers/LayerPanel.tsx`
- `app/client/src/lib/queries.ts`
- `app/client/src/types/api.ts`
- `app/server/src/types/api.py`
- `app/server/src/config/settings.py`
- `app/client/scripts/playwright_smoke.mjs`
- `app/server/tests/smoke_fixture_app.py`

Interpretation:

- They are integration surfaces, not clean single-lane ownership.
- They remain high-collision debt and need manual hunk review before any commit grouping.

## Shared compatibility contract and focused validation

Neutral contract doc:

- `app/docs/reporting-loop-package-contract.md`

Focused compatibility validation:

- `cmd /c npm.cmd run test:reporting-loop-package-contract`

Current intended scope:

- Aerospace fusion snapshot plus report brief
- Aerospace VAAC advisory report package as an adjacent reporting/support package
- Data AI fusion snapshot plus report brief
- Marine fusion snapshot plus report brief
- backend environmental fusion snapshot input remains covered by:
  - `python -m pytest app/server/tests/test_environmental_fusion_snapshot_input.py -q`

Adjacent but not yet first-class contract peers:

- backend webcam source-ops and sandbox-validation reporting surfaces such as:
  - `app/server/src/services/camera_sandbox_validation_report.py`
  - `app/server/src/services/camera_source_ops_candidate_network_summary.py`
  - `app/server/src/services/camera_source_ops_promotion_readiness_summary.py`
- current classification:
  - backend-only reporting/support surfaces
  - candidate-only, lifecycle/accounting, or import-readiness summaries
  - not yet first-class reporting-loop brief peers

Current contract interpretation:

- the contract is semantic, not schema-rigid
- current packages may preserve lineage directly, in metadata, or via a companion fusion-snapshot package
- current report briefs may expose `observe` / `orient` / `prioritize` / `explain` as an ordered section list or keyed section objects

## Runtime-boundary / review-only slices

These are real implemented backend/runtime surfaces, but they should still be described as bounded runtime or review infrastructure rather than reporting-desk proof.

- `app/server/src/routes/source_discovery.py`
- `app/server/src/services/source_discovery_service.py`
- `app/server/src/services/runtime_scheduler_service.py`
- `app/server/src/source_discovery/db.py`
- `app/server/src/source_discovery/models.py`
- `app/server/src/types/source_discovery.py`
- `app/server/src/routes/wave_llm.py`
- `app/server/src/services/wave_llm_service.py`
- `app/server/src/services/wave_llm_provider_config_service.py`
- `app/server/src/services/wave_llm_adapters.py`
- `app/server/src/services/media_evidence_service.py`
- `app/server/src/services/media_geolocation_eval_service.py`
- `app/server/src/services/analyst_workbench_service.py`
- `app/server/src/routes/analyst.py`
- `app/server/src/wave_monitor/models.py`

Current truth:

- Source Discovery has real bounded structure-scan, public-discovery, knowledge-backfill, review-claim import/apply, and media-evidence job surfaces.
- `app/docs/source-discovery-public-web-workflow.md` is a workflow/governance surface for that bounded public-web slice; it is not source-validation proof, approved-source status, or analyst-proof reporting evidence by itself.
- The Source Discovery route/service/types/test slice remains intentionally shared/runtime-scoped in current ownership scans; it should not be force-routed into a lane-local commit group just to reduce the `unknown` bucket.
- Wave LLM provider config and execution gating are real, but still review-only and budget/network/config constrained.
- Media fetch, OCR, and interpretation are bounded public-evidence scaffolding, not autonomous ingestion proof.
- Atlas media geolocation is derived-evidence and candidate-location scaffolding only; it does not become validation proof, trusted geolocation truth, or first-class reporting-loop package evidence by itself.
- Atlas media-geolocation hardening, including the evaluation harness and live benchmark manifest, is runtime-quality and derived-evidence scaffolding only; it is not analyst-proof reporting evidence, trusted geolocation truth, or source-validation proof.
- Wonder Stack Exchange queryless roots and seed-packet lineage are discovery/review infrastructure only; they remain candidate-routing and explainability metadata rather than source-trust, claim-truth, or reporting-loop proof.
- Wonder archive-index scans, mailing-list archive adapters, and curated directory-root or regional-portal discovery remain candidate/review/runtime only and do not become validation proof by landing in the repo.
- Wonder Statuspage and Mastodon discovery are bounded public-discovery/runtime surfaces only; discovered URLs and platform roots remain candidate/review metadata until separate controlled validation promotes them.
- Analyst workbench is a consumer/aggregation surface, not a claim-validation engine.

Still not valid to claim from these slices:

- autonomous source promotion
- automatic trust approval
- uncaveated media interpretation truth
- LLM-derived trusted facts
- harmful-action guidance

## Shared truth about stale source suggestions

The following should not be routed as fresh next-wave builds where repo truth already shows implementation:

- `propublica`
- `global-voices`
- `geonet-geohazards`
- `hko-open-weather`

Current interpretation:

- newer routing and ownership docs already reflect that these are implemented or otherwise no longer valid as “fresh source” suggestions
- older packet/history docs may still mention them and should be treated as superseded planning artifacts

## Current deconfliction summary

- Stable bounded reporting inputs already exist in Aerospace, Data AI, Marine, and Geospatial/Base Earth reference context.
- Shared frontend shell/inspector/query/type files remain the main collision risk.
- Shared runtime slices remain implemented but review-only/runtime-boundary surfaces, not full reporting-desk proof.
- Future reporting-desk work should compose existing bounded packages first rather than minting duplicate review/export/fusion helpers with overlapping semantics.

## Current larger assignment wave

- `connect`
  - `18:49` Source Discovery/runtime consolidation checkpoint is completed and the `19:15` shared reporting-loop contract wave is still in progress
- `data`
  - current-awareness digest, review/export coherence follow-on, topic-safe report export packet, and question-briefing packet are completed
- `marine`
  - current-awareness digest and source-row workflow closure packet are completed; the `19:35` question-briefing packet is still in progress
- `aerospace`
  - selected-target operational question packet, current-awareness digest, and reporting-handoff contract are completed; the `19:15` question-briefing packet is still in progress
- `geospatial`
  - Belgium RMI verification closed without implementation, the bounded `geoboundaries-admin` slice is completed, `meteoalarm-atom-feeds` is now implemented bounded warning context, and the `19:15` environmental question-briefing packet is completed
- `features-webcam`
  - source-ops portfolio digest, review-priority packet, and the `19:15` regional portfolio packet are completed

Current frontier note:

- the reporting-input stack above is now strong enough that the `2026-05-05 19:41 America/Chicago` source-expansion wave has landed materially and should no longer be routed as fresh intake
- that landed source-expansion wave is centered on:
  - `NOAA nowCOAST`
  - `National Weather Service Alerts API`
  - `RDAP`
  - `crt.sh`
  - `GPSJam`
  - `Navtex`
  - `OpenStreetMap` / `Overpass` / `Geofabrik` lead support

Guardrail:

- the next wave should build on the bounded reporting inputs above rather than reopen `propublica`, `global-voices`, `geonet-geohazards`, `hko-open-weather`, completed `world-news-awareness`, completed `dwd-cap-alerts`, completed VAAC report follow-through, completed marine report-brief work, completed Caltrans sandbox work, or the just-landed `nowCOAST`, `NWS Alerts`, `RDAP`, `crt.sh`, `GPSJam`, `Navtex`, or OSM lead-support work as fresh source builds

## Peer / runtime classification note

- Atlas media geolocation hardening remains peer and derived-evidence input only.
- Wonder Statuspage discovery remains candidate/review discovery input only.
- Wonder Mastodon discovery remains candidate/review discovery input only.
- Wonder Stack Exchange and seed-packet discovery remain candidate/review discovery input only.
- Wonder archive-index scan, mailing-list archive adapters, and curated directory or regional-portal scan remain candidate/review/runtime discovery input only.
- Source Discovery breadth and seed-packet lineage remain candidate/review/runtime or explainability-only input.
- media/OCR and geolocation runtime helpers remain peer, runtime, or derived-evidence input only.
- None of these peer/runtime slices change source implementation, source validation, or workflow-validation status by themselves.
