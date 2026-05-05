# Source Workflow Validation Plan

This plan defines what each implemented-but-not-validated Phase 2 source still needs before it can be promoted beyond `implemented`.

Purpose:

- keep `implemented` separate from `workflow-validated`
- define the missing evidence for each source
- prevent over-promotion on the assignment board
- give domain agents and Connect AI a deterministic validation bundle

Related docs:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md)
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md)
- [source-prompt-index.md](/C:/Users/mike/11Writer/app/docs/source-prompt-index.md)

Important rules:

- Do not promote any source in this document.
- This plan defines required evidence only.
- `implemented` means the slice exists in code.
- `workflow-validated` requires explicit workflow evidence.
- `fully validated` requires workflow evidence plus source-health and export behavior confirmation.
- Source discovery creates source candidates and starts source-memory learning; a discovered candidate is not an implemented source, validated source, live source, or scheduled connector.

Source discovery platform update:

- [source-discovery-platform-plan.md](/C:/Users/mike/11Writer/app/docs/source-discovery-platform-plan.md:1) defines 7Po8-style source discovery as a core 11Writer platform capability.
- [source-discovery-agent-framework.md](/C:/Users/mike/11Writer/app/docs/source-discovery-agent-framework.md:1) defines bounded discovery jobs, candidate-state handling, and no-hidden-crawler rules for implementation lanes.
- [source-discovery-reputation-governance-packet.md](/C:/Users/mike/11Writer/app/docs/source-discovery-reputation-governance-packet.md:1) defines the compact policy boundary for candidate states, reputation observations, claim outcomes, and shared source-memory routing.
- Discovery outputs must be tracked as candidate/source-review/source-memory evidence, not as source implementation proof.
- Any discovered candidate must preserve provenance, access result, machine-readability result, caveats, policy state, source-health state, source class, source reputation basis, wave-fit basis, duplicate checks, and owner recommendation before it can be routed for implementation.
- Correctness reputation must be evaluated separately from mission relevance.
- Static sources, live sources, full-text articles, social/image evidence, official sources, and community sources need different scoring and validation evidence.
- Claim outcomes such as confirmed, contradicted, corrected, outdated, unresolved, and not-applicable should drive learned source reputation.
- Validation promotion still requires the normal workflow-validation bundle below.
- Current repo-local source-memory routes and persistence are shared candidate/review/runtime evidence only; they do not directly create implemented or workflow-validated source rows.
- Source Discovery `structure-scan`, knowledge-node clustering/backfill, review-claim import/apply, Wave LLM provider/runtime controls, and media/OCR interpretation surfaces are candidate-routing, review, derived-evidence, or runtime-boundary helpers only; they do not create workflow-validation proof by themselves.

Marine workflow update:

- [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1) now records explicit workflow-validation evidence for:
  - `noaa-coops-tides-currents`
  - `noaa-ndbc-realtime`
  - `scottish-water-overflows`
- Explicit backend hardening evidence now also exists for:
  - `health=empty` on empty results
  - explicit fixture `sourceMode` on empty responses
  - `health=disabled` for disabled/non-fixture behavior
  - source-level caveat presence
  - request validation errors for invalid radius/coordinates
  - source-specific evidence-basis semantics
  - honest backend `unavailable` handling across the active marine context families
  - honest backend `degraded` handling only where partial-metadata evidence exists
- Treat those three as `workflow-validated` for status-tracking purposes.
- They still remain below `fully validated` and should not be treated as live validated from this evidence alone.
- `france-vigicrues-hydrometry` now has implemented backend-first source evidence plus completed hydrology/corridor report-follow-through in Marine AI progress, but it still remains below `workflow-validated` because no explicit source-row workflow-validation record is recorded yet.
- `netherlands-rws-waterinfo` now also has a completed bounded helper/export follow-on in Marine AI progress, but it still remains below `workflow-validated` because no explicit workflow-validation record is recorded yet.

Aerospace workflow update:

- [aerospace-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/aerospace-workflow-validation.md:1) now records explicit workflow-validation goals and export expectations for:
  - `noaa-aviation-weather-center-data-api`
  - `faa-nas-airport-status`
  - `nasa-jpl-cneos`
  - `noaa-swpc-space-weather`
  - `opensky-anonymous-states`
- Aerospace AI progress now also records the export-aware `Aerospace Context Review` summary and `aerospaceContextIssues` metadata path.
- Aerospace AI progress now also records workflow-supporting helper paths for:
  - `aerospaceContextReviewQueue`
  - `aerospaceContextReviewExportBundle`
  - `aerospaceWorkflowReadinessPackage`
- Backend contract tests, server compile, frontend lint, and frontend build are explicitly recorded as passing for the current aerospace lane.
- Executed browser smoke is still not recorded on this host because Playwright launch is currently classified as `windows-browser-launch-permission` before app assertions.
- Treat the five aerospace sources above as `implemented` and clearly `contract-tested`, but not `workflow-validated` from this evidence alone.

Data workflow update:

- Data AI progress now records backend-first implemented slices for:
  - `cisa-cyber-advisories`
  - `first-epss`
  - `nist-nvd-cve`
- Data AI progress now also records a conservative composition helper route for:
  - `cve-context`
- Data AI progress now also records a backend-first five-feed aggregate starter bundle for:
  - `cisa-cybersecurity-advisories`
  - `cisa-ics-advisories`
  - `sans-isc-diary`
  - `cloudflare-status`
  - `gdacs-alerts`
- Data AI progress now also records a backend-first official cyber advisory wave for:
  - `ncsc-uk-all`
  - `cert-fr-alerts`
  - `cert-fr-advisories`
- Data AI progress now also records a backend-first infrastructure/status wave for:
  - `cloudflare-radar`
  - `netblocks`
  - `apnic-blog`
- Data AI progress now also records a backend-first OSINT/investigations wave for:
  - `bellingcat`
  - `citizen-lab`
  - `occrp`
  - `icij`
- Data AI progress now also records a backend-first rights/civic/digital-policy wave for:
  - `eff-updates`
  - `access-now`
  - `privacy-international`
  - `freedom-house`
- Data AI progress now also records a backend-first fact-checking/disinformation wave for:
  - `full-fact`
  - `snopes`
  - `politifact`
  - `factcheck-org`
  - `euvsdisinfo`
- Data AI progress now also records a backend-first official/public advisories wave for:
  - `state-travel-advisories`
  - `eu-commission-press`
  - `un-press-releases`
  - `unaids-news`
- Data AI progress now also records a backend-first scientific/environmental context wave for:
  - `our-world-in-data`
  - `carbon-brief`
  - `eumetsat-news`
  - `smithsonian-volcano-news`
  - `eos-news`
- Data AI progress now also records a backend-first cyber-vendor/community follow-on wave for:
  - `google-security-blog`
  - `bleepingcomputer`
  - `krebs-on-security`
  - `securityweek`
  - `dfrlab`
- Data AI progress now also records a backend-first internet-governance/standards context wave for:
  - `ripe-labs`
  - `internet-society`
  - `lacnic-news`
  - `w3c-news`
  - `letsencrypt`
- Data AI progress now also records a backend-first public-institution/world-context wave for:
  - `who-news`
  - `undrr-news`
  - `nasa-breaking-news`
  - `noaa-news`
  - `esa-news`
  - `fda-news`
- Data AI progress now also records a backend-first cyber-institutional-watch-context wave for:
  - `cisa-news`
  - `jvn-en-new`
  - `debian-security`
  - `microsoft-security-blog`
  - `cisco-talos-blog`
  - `mozilla-security-blog`
  - `github-security-blog`
- All implemented Data feed waves above have fixture-backed routes, tests, compile evidence, and source-specific docs.
- The aggregate starter bundle has a bounded recent-items route, feed definition registry, RSS/Atom/RDF parser coverage, and prompt-injection-like fixture coverage.
- The official cyber advisory wave, infrastructure/status wave, OSINT/investigations wave, rights/civic/digital-policy wave, fact-checking/disinformation wave, official/public advisories wave, scientific/environmental context wave, cyber-vendor/community follow-on wave, internet-governance/standards context wave, public-institution/world-context wave, and cyber-institutional-watch-context wave use the same bounded recent-items route, feed registry, parser coverage, and prompt-injection-like fixture coverage.
- The NVD and CVE-context lane also preserves explicit evidence-class separation between metadata, advisory, prioritization, and discovery/feed text.
- Data AI progress now also records a backend-first review helper route at:
  - `/api/feeds/data-ai/source-families/review`
- Treat that review helper as metadata only, not as source truth or workflow-validation proof.
- Data AI progress now also records a backend-first family review queue route at:
  - `/api/feeds/data-ai/source-families/review-queue`
- Treat that review queue and export bundle as metadata only, not as source truth or workflow-validation proof.
- Data AI progress now also records a client-light inspector helper path at:
  - `dataAiSourceIntelligence`
- Data AI progress now also records a bounded topic/context lens and export-safe topic lines inside:
  - `dataAiSourceIntelligence`
- Data AI progress now also records a bounded report-brief package inside:
  - `dataAiSourceIntelligence`
- Data AI progress now also records a completed metadata-only infrastructure/status context package over:
  - `cloudflare-radar`
  - `netblocks`
  - `apnic-blog`
- Treat that consumer as metadata-only workflow support over readiness/review/review-queue surfaces, not as source truth or workflow-validation proof.
- None of these Data lanes should be treated as `workflow-validated` yet because no explicit consumer-path, smoke, or export-workflow validation is recorded.
- The active bounded Data AI feed lane should not be widened into broad polling; use [data-ai-next-routing-after-family-summary.md](/C:/Users/mike/11Writer/app/docs/data-ai-next-routing-after-family-summary.md) plus [data-ai-rss-batch3-routing-packets.md](/C:/Users/mike/11Writer/app/docs/data-ai-rss-batch3-routing-packets.md) for the next grouped Batch 3 expansion only after the implemented waves stay stable, starting with official/public advisories rather than reopening implemented fact-checking, OSINT, or rights/civic families.

Cross-lane helper update:

- Data AI progress now also records a backend-first family-overview helper route at:
  - `/api/feeds/data-ai/source-families/overview`
- Data AI progress now also records a backend-first family-review helper route at:
  - `/api/feeds/data-ai/source-families/review`
- Data AI progress now also records a backend-first family-review queue helper route at:
  - `/api/feeds/data-ai/source-families/review-queue`
- Data AI progress now also records a client-light inspector helper path at:
  - `dataAiSourceIntelligence`
- Geospatial AI progress now also records a backend-first environmental weather/observation review queue route at:
  - `/api/context/environmental/weather-observation-review-queue`
- Geospatial AI progress now also records a backend-first environmental weather/observation export bundle route at:
  - `/api/context/environmental/weather-observation-export-bundle`
- Geospatial AI progress now also records a backend-first environmental family-overview helper route at:
  - `/api/context/environmental/source-families-overview`
- Geospatial AI progress now also records a backend-first environmental family export helper route at:
  - `/api/context/environmental/source-families-export`
- Geospatial AI progress now also records a backend-first environmental context export package route at:
  - `/api/context/environmental/context-export-package`
- Geospatial AI progress now also records a backend-first environmental situation snapshot package route at:
  - `/api/context/environmental/situation-snapshot-package`
- Geospatial AI progress now also records a backend-first environmental fusion-snapshot input route at:
  - `/api/context/environmental/fusion-snapshot-input`
- Marine AI progress now also records a workflow-supporting export helper path at:
  - `marineAnomalySummary.contextIssueExportBundle`
- Marine AI progress now also records a full review/export coherence regression over `marineAnomalySummary` helper outputs
- Marine AI progress now also records focused replay-evidence and evidence-interpretation export coherence checks over `marineAnomalySummary`
- Marine AI progress now also records timeline-snapshot preservation of chokepoint review-lens metadata plus coherence between timeline snapshots and chokepoint review package outputs
- Marine AI progress now also records a completed hydrology/source-health workflow helper path at:
  - `marineAnomalySummary.hydrologySourceHealthWorkflow`
- Treat that hydrology/source-health package as implemented workflow-supporting metadata only; it now has build/lint/smoke/helper evidence, but it still remains below `workflow-validated`
- Marine AI progress now also records a completed bounded report/export helper path at:
  - `marineAnomalySummary.hydrologySourceHealthReport`
- Treat that report package as implemented workflow-supporting metadata only; it now has regression and smoke-metadata evidence, but it still remains below `workflow-validated`
- Marine AI progress now also records a completed fusion-snapshot input helper path at:
  - `marineAnomalySummary.fusionSnapshotInput`
- Treat that fusion input as implemented workflow-supporting metadata only; it now has regression and smoke-metadata evidence, but it still remains below `workflow-validated`
- Aerospace AI progress now also records a workflow-supporting review helper path at:
  - `aerospaceContextGapQueue`
- Aerospace AI progress now also records a workflow-supporting current-vs-archive separation helper path at:
  - `aerospaceCurrentArchiveContext`
- Aerospace AI progress now also records a workflow-supporting export coherence helper path at:
  - `aerospaceExportCoherence`
- Aerospace AI progress now also records a compact report/export metadata helper path at:
  - `aerospaceContextSnapshotReport`
- Aerospace AI progress now also records a workflow-readiness and evidence-accounting helper path at:
  - `aerospaceWorkflowReadinessPackage`
- Aerospace AI progress now also records a completed workflow-validation evidence snapshot helper path at:
  - `aerospaceWorkflowValidationEvidenceSnapshot`
- Aerospace AI progress now also records a workflow-supporting review/export helper path at:
  - `aerospaceContextReviewQueue`
  - `aerospaceContextReviewExportBundle`
- Aerospace AI progress now also records a completed report-brief package helper path at:
  - `aerospaceReportBriefPackage`
- Features/Webcam AI progress now also records a workflow-supporting evidence-packet selector route at:
  - `/api/cameras/source-ops-evidence-packets`
- Features/Webcam AI progress now also records a workflow-supporting aggregate export-bundle route at:
  - `/api/cameras/source-ops-evidence-packets-export-bundle`
- Features/Webcam AI progress now also records a workflow-supporting aggregate handoff-summary route at:
  - `/api/cameras/source-ops-evidence-packets-handoff-summary`
- Features/Webcam AI progress now also records a workflow-supporting aggregate export surface route at:
  - `/api/cameras/source-ops-export-surface`
- Features/Webcam AI progress now also records `nsw-live-traffic-cameras` and `quebec-mtmd-traffic-cameras` as `candidate-sandbox-importable` only; that is source-ops evidence and not implementation or validation proof.
- Features/Webcam AI progress now also records `baton-rouge-traffic-cameras` and `vancouver-web-cam-url-links` as `candidate-sandbox-importable`, `arlington-traffic-cameras` as `endpoint-verified` only, and `qldtraffic-web-cameras` as held after a `401` on `/v1/webcams`; that remains candidate/source-ops evidence rather than implementation or validation proof.
- Features/Webcam AI progress now also records a backend-only sandbox-candidate review-burden and source-health-expectation summary over current candidate-sandbox-importable sources.
- Atlas AI progress now also records a fixture-backed Wave Monitor tool surface at:
  - `/api/tools/waves/overview`
- Atlas AI progress now also records shared analyst/readiness integration for:
  - `tool-wave-monitor`
- Atlas AI progress now also records a shared source-memory backend surface at:
  - `/api/source-discovery/memory/overview`
  - `/api/source-discovery/memory/candidates`
  - `/api/source-discovery/memory/claim-outcomes`
  - `/api/source-discovery/jobs/seed-url`
  - `/api/source-discovery/jobs/record-source-extract`
  - `/api/source-discovery/health/check`
  - `/api/source-discovery/jobs/expand`
  - `/api/source-discovery/jobs/feed-link-scan`
  - `/api/source-discovery/content/snapshots`
  - `/api/source-discovery/reputation/reverse-event`
  - `/api/source-discovery/scheduler/tick`
  - `/api/source-discovery/review/queue`
  - `/api/source-discovery/review/actions`
  - `/api/source-discovery/runtime/status`
- Atlas AI progress now also records a newer Source Discovery Ten-Step backend slice as peer/runtime input only.
- Atlas alerting and current next-task routing now also record a newer runtime operator-console slice as peer/runtime input only pending Connect validation.
- Atlas alerting now also records a media-geolocation peer slice; keep it at derived-evidence or candidate-location input only unless a later controlled validation pass explicitly promotes a narrower surface.
- Wonder alerting now also records bounded Statuspage and Mastodon discovery; keep both at candidate/review discovery input only unless a later controlled validation pass explicitly promotes a narrower surface.
- Wonder planning docs now also record Browser Use guidance plus macOS/plugin/connector planning, but those remain peer planning input only and must not change source-validation posture by themselves.
- These helper paths are implemented and useful for review/export workflows, but they should not be treated as external-source workflow validation proof by themselves.
- Current evidence split:
  - scientific/environmental context is implemented and contract-tested on the existing shared Data AI route, but still has no explicit consumer-path or workflow-validation record
  - official/public advisories is implemented and contract-tested on the existing shared Data AI route, but still has no explicit consumer-path or workflow-validation record
  - source-family review queue is implemented and contract-tested as review metadata only, but still has no explicit consumer-path or workflow-validation record
  - Data AI Source Intelligence is implemented as a client-light metadata-only inspector consumer, and its topic/context lens plus export-safe topic lines remain metadata-only workflow support without explicit smoke or manual workflow-validation record
  - the infrastructure/status context package over `cloudflare-radar`, `netblocks`, and `apnic-blog` is now completed workflow-supporting metadata, not the active fresh Data lane
  - the latest completed Data lanes now include the bounded fusion/claim-integrity snapshot and bounded report-brief package over the existing metadata-only Data AI surfaces
  - the next useful Data move is one bounded topic-scoped report packet plus reporting-input coherence and validation/export closure; do not reopen implemented infrastructure/status, completed `world-news-awareness`, `propublica`, or `global-voices` as fresh source-build lanes
  - cyber-vendor/community follow-on is implemented and contract-tested on the existing shared Data AI route, but still has no explicit consumer-path or workflow-validation record
  - internet-governance/standards context is implemented and contract-tested on the existing shared Data AI route, but still has no explicit consumer-path or workflow-validation record
  - public-institution/world-context is implemented and contract-tested on the existing shared Data AI route, but still has no explicit consumer-path or workflow-validation record
  - Data family overview helper is contract-tested and metadata-oriented only
  - environmental family overview helper, environmental family export helper, environmental context export package, environmental situation snapshot package, environmental weather/observation review queue, and environmental weather/observation export bundle are contract-tested and metadata-oriented only
  - marine issue export bundle plus full export coherence, focused-evidence coherence, timeline/chokepoint coherence regressions, the hydrology/source-health workflow helper, the hydrology/source-health report helper, and `marineFusionSnapshotInput` now have helper regression plus marine smoke/build evidence, but remain helper-package evidence rather than source promotion
  - aerospace context gap queue, current-vs-archive helper, export-coherence helper, context snapshot report helper, and workflow-readiness package have smoke assertions prepared or export-aware evidence, but executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`
  - aerospace context review queue, export bundle, workflow-validation evidence snapshot, and report-brief package have prepared smoke assertions or export-aware accounting evidence, but executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`; preserve the stale assignment-marker caveat on the snapshot helper and the Marine-owned lint-failure note from the last aerospace run
  - Features/Webcam evidence-packet selector, aggregate export bundle, aggregate handoff summary, and aggregate export surface have backend test and documentation evidence, but no explicit end-to-end workflow note yet
  - Features/Webcam sandbox-candidate review-burden/source-health summary has backend test and documentation evidence, and the current candidate-expansion wave appears completed with Baton Rouge/Vancouver/Caltrans candidate-sandbox-importable, Arlington endpoint-verified or feasibility-only, NZTA feasibility-only, and Queensland held; the newer active Features/Webcam lane is now NZTA and Arlington feasibility plus bounded candidate growth, but no explicit end-to-end workflow note is recorded yet
  - Wave Monitor is implemented as a fixture-backed tool surface with focused backend tests and analyst/readiness integration, but it is still not a validated live runtime, scheduler, or source-truth surface
  - source discovery runtime is implemented as a shared backend candidate/reputation surface with focused backend tests plus bounded seed, health, expand, snapshot, reversal, and manual scheduler-tick primitives, but it is still not source implementation proof, source-truth proof, autonomous discovery proof, or workflow-validation proof
  - the Atlas runtime operator-console slice remains peer/runtime input only until Connect records explicit current-state validation; do not route it as workflow-validation proof, source proof, or ownership proof

Wave Monitor tool update:

- [7po8-integration-plan.md](/C:/Users/mike/11Writer/app/docs/7po8-integration-plan.md:1) plus Atlas AI progress now record a fixture-backed Wave Monitor route at `/api/tools/waves/overview`.
- Atlas AI progress now also records `tool-wave-monitor` integration into analyst evidence-timeline and source-readiness surfaces.
- Treat Wave Monitor as an implemented tool surface and shared architecture input, not a source row and not a separate runtime.
- Persistent storage, live connector execution, scheduler behavior, and Situation Workspace UI still remain outside current implemented proof.
- Atlas evidence should inform governance and validation notes, but Atlas remains user-directed and does not by itself assign stable ownership.

Source discovery memory update:

- [source-discovery-platform-plan.md](/C:/Users/mike/11Writer/app/docs/source-discovery-platform-plan.md:1), [source-discovery-agent-framework.md](/C:/Users/mike/11Writer/app/docs/source-discovery-agent-framework.md:1), and Atlas AI progress now record a shared source-discovery runtime with overview, candidate-write, claim-outcome update, seed-url, record-source-extract, health-check, bounded expand, feed-link-scan, snapshot, reversal, review queue/actions, runtime status, and manual scheduler-tick routes.
- Current repo evidence supports persistence models, SQLite-backed session wiring, deterministic claim-outcome reputation updates, Wave Monitor candidate seeding, metadata-only health checks, bounded expansion jobs, content snapshots, review queue/actions, runtime status, and reputation reversal.
- Connect AI progress now also records `runtime_scheduler_service.py` as conservative compatibility and status plumbing rather than proof of hidden background scheduling.
- Connect AI progress now also records provider/runtime boundary truth where config presence is exposed by key-source name only, `fixture` remains deterministic and review-only, and `openai`, `OpenRouter`, `Anthropic`, `xAI`, `Google`, `OpenClaw`, and `ollama` remain gated by provider configuration, explicit network permission, and positive request budget.
- Mock-model paths remain deterministic and no provider path is allowed to promote sources, validate claims, activate connectors, or create direct action guidance.
- Treat source discovery memory as an implemented shared candidate/reputation surface and governance input, not a source row and not a validated discovery runtime.
- Autonomous discovery runners, hidden live polling, automatic source approval, and frontend review workflows remain outside current implemented proof.
- Atlas evidence should inform governance and validation notes, but Atlas remains user-directed and does not by itself assign stable ownership or validation status.

Recent geospatial/aerospace source-build update:

- `geosphere-austria-warnings` now exists as a backend-first implemented geospatial warning slice with fixture-backed contracts and docs.
- `nasa-power-meteorology-solar` now exists as a backend-first implemented geospatial modeled-context slice with fixture-backed contracts and docs.
- `natural-earth-physical` now exists as a backend-first implemented geospatial static/reference slice with fixture-backed contracts and docs.
- `gshhg-shorelines` now exists as a backend-first implemented geospatial static/reference shoreline slice with fixture-backed contracts and docs.
- `noaa-global-volcano-locations` now exists as a backend-first implemented geospatial static/reference slice with fixture-backed contracts and docs.
- `pb2002-plate-boundaries` now exists as a backend-first implemented geospatial static/reference tectonic-context slice with fixture-backed contracts and docs.
- `taiwan-cwa-aws-opendata` now exists as a backend-first implemented geospatial observed/context slice with fixture-backed contracts and docs.
- `nrc-event-notifications` now exists as a backend-first implemented geospatial source-reported/context slice with fixture-backed contracts, docs, and prompt-injection-safe free-text coverage.
- `bmkg-earthquakes` now exists as a backend-first implemented geospatial regional-authority earthquake slice with fixture-backed contracts, source-health fields, and prompt-injection-safe free-text coverage.
- `ga-recent-earthquakes` now exists as a backend-first implemented geospatial regional-authority KML earthquake slice with fixture-backed contracts and docs.
- `emsc-seismicportal-realtime` now exists as a backend-first implemented geospatial buffered event-context slice with fixture-backed contracts and docs.
- `orfeus-eida-federator` now exists as a backend-first implemented geospatial bounded federated seismic station-metadata slice with fixture-backed contracts and docs.
- `ourairports-reference` now has a bounded selected-target/export consumer through `useOurAirportsReferenceQuery` and `ourairportsReferenceContext`, but it remains below workflow validation.
- `washington-vaac-advisories`, `anchorage-vaac-advisories`, and `tokyo-vaac-advisories` now exist as an implemented aerospace advisory package with fixture-backed contracts plus bounded client/export consumption.
- None of the geospatial/aerospace updates above should be treated as `workflow-validated` yet because no executed consumer-path or smoke/export validation record is explicit on this host.

## Suggested Validation Ownership

- Geospatial sources
  - `Geospatial AI` owns primary workflow validation when the source lands in geospatial layers, inspectors, or evidence flows.
  - `Connect AI` may perform final cross-repo validation confirmation.
- Marine sources
  - `Marine AI` owns primary workflow validation for marine context, summary, and evidence/export behavior.
  - `Connect AI` may perform final cross-repo validation confirmation.
- Aerospace sources
  - `Aerospace AI` owns primary workflow validation for inspector, context, and export behavior.
  - `Connect AI` may perform final cross-repo validation confirmation.
- Cross-domain shared smoke/export
  - `Connect AI` owns release-grade smoke, shared export checks, and repo-wide validation notes.

## Minimum Workflow-Validation Bundle

Every source should have this minimum bundle before promotion to `workflow-validated`:

- backend contract tests pass
- frontend build/lint pass when relevant repo-wide validation is rerun
- source appears in minimal operational UI
- source health or source mode is visible where the slice exposes it
- selected item inspector or detail workflow works if applicable
- export metadata contains source summary and caveat fields
- smoke phase or a deterministic manual workflow is documented
- no overclaiming caveats are missing

## Promotion Rules

### `implemented` -> `workflow-validated`

Required:

- implementation already present in repo
- contract tests pass for the source slice
- minimal UI or operational consumer path is exercised successfully
- source health and freshness state are visible or intentionally absent with documented reason
- export metadata for the source path is checked and recorded if exports exist
- deterministic smoke or manual validation steps are recorded in a doc, agent report, or release note

### `workflow-validated` -> `fully validated`

Required:

- all `workflow-validated` criteria
- explicit confirmation that export metadata is complete and correct
- explicit confirmation that caveat language survives UI and export paths
- explicit confirmation that fixture mode and live-mode assumptions are both documented
- explicit confirmation that source-health behavior is correct under normal and stale/unavailable conditions when the slice exposes those states

## Per-Source Plans

### `usgs-volcano-hazards`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/events/volcanoes/recent`
  - test `app/server/tests/test_volcano_events.py`
  - fixture `app/server/data/usgs_volcano_status_fixture.json`
  - client hook `useVolcanoStatusQuery`
  - map/inspector/app-shell consumption noted in repo evidence
- Missing workflow evidence:
  - explicit recorded walkthrough of layer load, item selection, and export behavior
  - explicit source-health visibility confirmation
- Required UI/smoke checks:
  - volcano layer renders from fixture-backed or deterministic data path
  - selecting a volcano event opens the expected inspector/details path
  - alert level and caveat language remain visible
- Required export metadata checks:
  - export includes `sourceId`, source name, observed time, fetched time, and caveat text
  - export does not overclaim plume, ash, or route impact
- Source health checks:
  - freshness or update status is visible if exposed
  - stale or unavailable wording is bounded and does not imply no hazard
- Fixture/live mode checks:
  - fixture path matches the contract test payload
  - live-mode verification steps are documented separately from automated tests
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_volcano_events.py -q`
- Pass criteria for `workflow-validated`:
  - contract test passes
  - layer and inspector path are manually or smoke-validated
  - export metadata fields are checked once and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health behavior and stale-state wording are explicitly validated
  - export caveats are confirmed correct in a saved validation note
- Known blockers:
  - no explicit workflow-validation record exists yet

### `usgs-geomagnetism`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/context/geomagnetism/usgs`
  - test `app/server/tests/test_usgs_geomagnetism.py`
  - fixture `app/server/data/usgs_geomagnetism_fixture.json`
  - client hook `useUsgsGeomagnetismContextQuery`
  - source-specific doc `app/docs/environmental-events-usgs-geomagnetism.md`
  - Geospatial AI progress records explicit source-health and export-facing metadata fields in the backend response
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health rendering confirmation in any frontend path
- Required UI/smoke checks:
  - one bounded consumer path shows observatory id, requested interval, and caveat text
  - no consumer path turns geomagnetic values into impact or failure claims
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, observatory id, interval bounds, fetched time, and caveat text
  - export preserves observational/contextual semantics only
- Source health checks:
  - freshness or generated-time wording is visible if surfaced
  - empty and invalid-request behavior remain distinct from unavailable or disabled states
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with `test_usgs_geomagnetism.py`
  - any live-mode verification stays manual and bounded to the documented current-day request scope
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_usgs_geomagnetism.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `natural-earth-physical`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/context/reference/natural-earth/physical/land`
  - test `app/server/tests/test_base_earth_reference_bundle.py`
  - fixture `app/server/data/natural_earth_physical_land_fixture.json`
  - source-specific doc `app/docs/environmental-events-natural-earth-physical.md`
  - Geospatial AI progress records explicit backend-first static/reference behavior and source-caveat preservation
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health or source-mode rendering confirmation in any frontend path
- Required UI/smoke checks:
  - one bounded consumer path shows theme, version, feature counts or selected feature context, and caveat text
  - no consumer path turns static physical vectors into live hazard or legal-boundary truth
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, theme or layer identifier, fetched time, release/version metadata when present, and caveat text
  - export preserves static/reference semantics only
- Source health checks:
  - empty, unavailable, and invalid-filter behavior remain distinct where surfaced
  - source-health wording does not imply live observation freshness
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with `test_base_earth_reference_bundle.py`
  - any live-mode verification stays manual and bounded to the pinned Natural Earth physical theme only
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_base_earth_reference_bundle.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `noaa-global-volcano-locations`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/context/reference/noaa-global-volcanoes`
  - test `app/server/tests/test_base_earth_reference_bundle.py`
  - fixture `app/server/data/noaa_global_volcano_locations_fixture.json`
  - source-specific doc `app/docs/environmental-events-noaa-global-volcano-locations.md`
  - Geospatial AI progress records explicit backend-first static/reference volcano metadata behavior and source-caveat preservation
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health or source-mode rendering confirmation in any frontend path
- Required UI/smoke checks:
  - one bounded consumer path shows volcano name, location, type, and caveat text
  - no consumer path turns static volcano-reference data into current eruption or ash-impact truth
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, volcano identifier or name, fetched time, static/reference metadata fields, and caveat text
  - export preserves static/reference semantics only
- Source health checks:
  - empty, unavailable, and invalid-filter behavior remain distinct where surfaced
  - source-health wording does not imply live volcano-status freshness
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with `test_base_earth_reference_bundle.py`
  - any live-mode verification stays manual and bounded to the pinned NOAA global volcano reference file only
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_base_earth_reference_bundle.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `geosphere-austria-warnings`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/events/geosphere-austria/warnings`
  - test `app/server/tests/test_geosphere_austria_warnings.py`
  - fixture `app/server/data/geosphere_austria_warnings_fixture.json`
  - source-specific doc `app/docs/environmental-events-geosphere-austria-warnings.md`
  - Geospatial AI progress records explicit advisory semantics, source health, and bounded backend route behavior
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health rendering confirmation in any frontend path
- Required UI/smoke checks:
  - one bounded consumer path shows warning type, source-native severity/color, area text, time windows, and caveat text
  - no consumer path turns warning records into impact, damage, or closure proof
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, fetched time, warning count or selected-record summary, and caveat text
  - export preserves advisory/contextual semantics only
- Source health checks:
  - freshness or generated-time wording is visible if surfaced
  - empty and invalid-filter behavior remain distinct from unavailable or disabled states
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with `test_geosphere_austria_warnings.py`
  - any live-mode verification stays manual and bounded to the documented current warning feed
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_geosphere_austria_warnings.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `cisa-cyber-advisories`

- Owner agent:
  - `Data AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/context/cyber/cisa-advisories/recent`
  - test `app/server/tests/test_cisa_cyber_advisories.py`
  - fixture `app/server/data/cisa_cybersecurity_advisories_fixture.xml`
  - source-specific doc `app/docs/cyber-context-sources.md`
  - Data AI progress records explicit advisory-only caveats, source health, dedupe behavior, and export-facing metadata fields
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health rendering or operational-consumer confirmation
- Required UI/smoke checks:
  - one bounded consumer path shows advisory id, title, published time, source mode or health where surfaced, and caveat text
  - no consumer path turns advisory items into exploit, compromise, victim, or impact confirmation
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, feed URL, final URL when present, advisory id or GUID, published time, fetched time, evidence basis, and caveat text
  - export preserves advisory/source-reported semantics only
- Source health checks:
  - parse failure, empty feed, and unavailable-source behavior remain distinct where surfaced
  - dedupe behavior does not silently drop provenance fields
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with `test_cisa_cyber_advisories.py`
  - injection-like fixture coverage should remain part of the bounded feed-family validation path
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_cisa_cyber_advisories.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language and injection-safe text handling are confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `first-epss`

- Owner agent:
  - `Data AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/context/cyber/first-epss`
  - test `app/server/tests/test_first_epss.py`
  - fixture `app/server/data/first_epss_fixture.json`
  - source-specific doc `app/docs/cyber-context-sources.md`
  - Data AI progress records explicit scored-context caveats, source health, request parsing, and export-facing metadata fields
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health rendering or operational-consumer confirmation
- Required UI/smoke checks:
  - one bounded consumer path shows CVE id, EPSS score, percentile, date when present, and caveat text
  - no consumer path turns EPSS output into exploit proof, incident truth, or required action
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, request parameters, source URL, fetched time, evidence basis, and caveat text
  - export preserves scored/context semantics only
- Source health checks:
  - invalid request, empty result, and unavailable-source behavior remain distinct where surfaced
  - source-health wording does not overstate data completeness
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with `test_first_epss.py`
  - live-mode assumptions remain documented separately from automated tests
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_first_epss.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `nist-nvd-cve`

- Owner agent:
  - `Data AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/context/cyber/nvd-cve`
  - supporting composition route `/api/context/cyber/cve-context`
  - tests `app/server/tests/test_nvd_cve.py` and `app/server/tests/test_cve_context.py`
  - fixture `app/server/data/nvd_cve_fixture.json`
  - source-specific doc `app/docs/cyber-context-sources.md`
  - Data AI progress records explicit evidence-class separation between NVD metadata, CISA advisory fields, EPSS scoring, and feed/discovery text
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health rendering or operational-consumer confirmation
- Required UI/smoke checks:
  - one bounded consumer path shows CVE id, published/updated time, CVSS metadata when present, and caveat text
  - the consumer path keeps NVD metadata, CISA advisories, EPSS scores, and feed/discovery context semantically separate
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, request parameters, NVD item identifiers, published or updated time, fetched time, evidence basis, and caveat text
  - export preserves metadata/context semantics only
- Source health checks:
  - invalid request, empty result, and unavailable-source behavior remain distinct where surfaced
  - source-health wording does not imply high-rate completeness or bulk-sync coverage
- Fixture/live mode checks:
  - fixtures remain deterministic and aligned with `test_nvd_cve.py` and `test_cve_context.py`
  - prompt-injection-like fixture coverage for NVD free-text descriptions and references remains part of the bounded validation path
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_nvd_cve.py -q`
  - `python -m pytest app/server/tests/test_cve_context.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - evidence-class separation and caveat language are confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `taiwan-cwa-aws-opendata`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/context/weather/taiwan-cwa`
  - test `app/server/tests/test_taiwan_cwa_weather.py`
  - fixture `app/server/data/taiwan_cwa_current_weather_fixture.json`
  - source-specific doc `app/docs/environmental-events-taiwan-cwa-weather.md`
  - Geospatial AI progress records bounded AWS-file-family behavior, observed/context semantics, and explicit source-health fields
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health rendering confirmation in any frontend path
- Required UI/smoke checks:
  - one bounded consumer path shows station id, observed time, coordinates when present, weather values, and caveat text
  - no consumer path turns the slice into warning, impact, damage, flooding, or disruption claims
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, station id, observed time, fetched time, file-family metadata, and caveat text
  - export preserves observed/context semantics only
- Source health checks:
  - freshness or source-generated-time wording is visible if surfaced
  - empty and invalid-filter behavior remain distinct from unavailable or disabled states
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with `test_taiwan_cwa_weather.py`
  - any live-mode verification stays manual and bounded to the documented AWS-backed file family only
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_taiwan_cwa_weather.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `nrc-event-notifications`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/events/nrc/recent`
  - test `app/server/tests/test_nrc_event_notifications.py`
  - fixture `app/server/data/nrc_event_notifications_fixture.xml`
  - source-specific doc `app/docs/environmental-events-nrc-event-notifications.md`
  - Geospatial AI progress records bounded RSS/event-notification behavior and prompt-injection-safe free-text fixture coverage
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health rendering confirmation in any frontend path
- Required UI/smoke checks:
  - one bounded consumer path shows title, organization or facility text, event time when present, and caveat text
  - no consumer path turns source-reported event notices into radiological impact, closure, or public-safety proof
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, source URL, item id or GUID, published time when present, fetched time, and caveat text
  - export preserves source-reported/context semantics only
- Source health checks:
  - parse failure, empty feed, and unavailable-source behavior remain distinct where surfaced
  - source-health wording must not overstate operational certainty
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with `test_nrc_event_notifications.py`
  - injection-like fixture coverage remains part of the bounded validation path
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_nrc_event_notifications.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language and injection-safe text handling are confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `bmkg-earthquakes`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/events/bmkg-earthquakes/recent`
  - test `app/server/tests/test_bmkg_earthquakes.py`
  - fixture `app/server/data/bmkg_earthquakes_fixture.json`
  - source-specific doc `app/docs/environmental-events-bmkg-earthquakes.md`
  - Geospatial AI progress records explicit source-health fields, caveats, and prompt-injection-safe free-text coverage
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health rendering confirmation in any frontend path
- Required UI/smoke checks:
  - one bounded consumer path shows magnitude, location text, time, and caveat text
  - no consumer path turns BMKG records into tsunami, damage, or casualty claims without source support
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, event identifier, event time, fetched time, source URL, and caveat text
  - export preserves observed/source-reported earthquake semantics only
- Source health checks:
  - freshness or source-generated-time wording is visible if surfaced
  - empty and invalid-filter behavior remain distinct from unavailable or disabled states
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with `test_bmkg_earthquakes.py`
  - prompt-injection-like fixture coverage for free-text location fields remains part of the bounded validation path
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_bmkg_earthquakes.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language and injection-safe text handling are confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `ga-recent-earthquakes`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/events/ga-earthquakes/recent`
  - test `app/server/tests/test_ga_recent_earthquakes.py`
  - fixture `app/server/data/ga_recent_earthquakes_fixture.kml`
  - source-specific doc `app/docs/environmental-events-ga-recent-earthquakes.md`
  - Geospatial AI progress records bounded KML parsing and regional-authority provenance
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health rendering confirmation in any frontend path
- Required UI/smoke checks:
  - one bounded consumer path shows event location, time, magnitude when present, and caveat text
  - no consumer path turns sparse KML records into richer impact semantics than the source supports
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, event identifier or title, event time, fetched time, source URL, and caveat text
  - export preserves KML regional-authority event semantics only
- Source health checks:
  - freshness or source-generated-time wording is visible if surfaced
  - empty and invalid-filter behavior remain distinct from unavailable or disabled states
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with `test_ga_recent_earthquakes.py`
  - any live-mode verification stays manual and bounded to the documented Geoscience Australia KML feed only
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_ga_recent_earthquakes.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `nasa-power-meteorology-solar`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/context/weather/nasa-power`
  - test `app/server/tests/test_nasa_power_meteorology_solar.py`
  - fixture `app/server/data/nasa_power_meteorology_solar_fixture.json`
  - source-specific doc `app/docs/environmental-events-nasa-power-meteorology-solar.md`
  - Geospatial AI progress records explicit modeled-context semantics, source health, and bounded point-query behavior
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export-metadata validation note
  - explicit source-health rendering confirmation in any frontend path
- Required UI/smoke checks:
  - one bounded consumer path shows coordinates, parameter set, date range, and caveat text
  - no consumer path presents modeled values as observed local weather or event truth
  - empty or unavailable branch remains intelligible
- Required export metadata checks:
  - export includes source id, coordinates, parameter set, date range, fetched time, and caveat text
  - export preserves modeled/contextual semantics only
- Source health checks:
  - freshness or generated-time wording is visible if surfaced
  - empty and invalid-request behavior remain distinct from unavailable or disabled states
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with `test_nasa_power_meteorology_solar.py`
  - any live-mode verification stays manual and bounded to the documented point-query scope
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_nasa_power_meteorology_solar.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `noaa-coops-tides-currents`

- Owner agent:
  - `Marine AI`
- Current validation level:
  - `workflow-validated`
- Existing evidence:
  - route `/api/marine/context/noaa-coops`
  - test `app/server/tests/test_marine_contracts.py`
  - fixture-backed marine context in `app/server/tests/smoke_fixture_app.py`
  - client hook `useMarineNoaaCoopsContextQuery`
  - downstream marine summary/export usage noted in repo evidence
  - explicit contract guarantees in [marine-context-source-contract-matrix.md](/C:/Users/mike/11Writer/app/docs/marine-context-source-contract-matrix.md:1)
  - explicit workflow evidence in [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1)
  - CO-OPS observations preserve `observed` evidence basis semantics
- Missing workflow evidence:
  - remaining gap is full-validation confirmation for `unavailable` or `degraded` source-health behavior and any live-mode caveat handling
- Required UI/smoke checks:
  - marine context path displays station metadata and latest observation values
  - no prediction text is presented as observation
  - empty/unavailable branch is intelligible if no nearby station is returned
- Required export metadata checks:
  - export includes source id, station id, datum, units, observed time, fetched time, and caveats
  - export preserves observed-vs-context distinction
- Source health checks:
  - empty and disabled contract behavior is already covered at the backend contract layer
  - metadata endpoint and observation endpoint health are not conflated if separately surfaced
  - stale observation time is visible or represented in caveat text
- Fixture/live mode checks:
  - marine contracts test remains the authoritative contract check
  - fixture mode is explicit in current contract coverage, including empty responses
  - smoke fixture app path should cover deterministic CO-OPS context rendering
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - marine contract tests pass
  - marine context panel or evidence consumer shows CO-OPS fields correctly
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - stale station behavior and source-health wording are explicitly checked
  - deterministic fixture path and live-mode assumptions are documented together
  - `unavailable` or `degraded` behavior confirmation and live-mode assumption confirmation are explicitly recorded
- Known blockers:
  - no blocker for workflow-validated status
  - remaining work is only for any promotion beyond workflow-validated

### `noaa-aviation-weather-center-data-api`

- Owner agent:
  - `Aerospace AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/aviation-weather/airport-context`
  - test `app/server/tests/test_aviation_weather_contracts.py`
  - client hook `useAviationWeatherContextQuery`
  - inspector/app-shell usage noted in repo evidence
  - aerospace workflow docs now include `aviationWeatherContext` plus `aerospaceContextIssues` export-path expectations
  - backend contracts, compile, lint, and build are explicitly recorded as passing
- Missing workflow evidence:
  - explicit inspector validation for METAR plus TAF rendering
  - explicit export metadata validation
  - explicit fixture provenance note because no dedicated `app/server/data` fixture file was found in the audit
- Required UI/smoke checks:
  - airport context renders METAR and TAF in the expected consumer path
  - observed and forecast labels remain distinct
  - unavailable or stale state is clear
- Required export metadata checks:
  - export includes station/ICAO id, METAR observed time, TAF issued or valid time, source id, and caveat text
  - export does not collapse METAR and TAF into one evidence class
- Source health checks:
  - freshness distinguishes observed METAR from forecast TAF timing
  - endpoint or source mode health is visible if exposed
- Fixture/live mode checks:
  - contract test payloads stay deterministic
  - live curl checks are documented as manual verification only
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_aviation_weather_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - inspector or airport context workflow is exercised successfully
  - export path is checked once and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and stale-state behavior are explicitly checked
  - fixture provenance and live-mode assumptions are documented cleanly
- Known blockers:
  - no explicit workflow-validation record exists
  - dedicated fixture-file traceability is weaker than for some other sources
  - executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`

### `faa-nas-airport-status`

- Owner agent:
  - `Aerospace AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/aerospace/airports/{airport_code}/faa-nas-status`
  - test `app/server/tests/test_faa_nas_status_contracts.py`
  - fixture `app/server/data/faa_nas_airport_status_fixture.xml`
  - client hook `useFaaNasAirportStatusQuery`
  - inspector/app-shell usage noted in repo evidence
  - aerospace workflow docs now include `faaNasAirportStatus` plus `aerospaceContextIssues` export-path expectations
  - backend contracts, compile, lint, and build are explicitly recorded as passing
- Missing workflow evidence:
  - explicit airport inspector or context validation note
  - explicit export metadata validation note
- Required UI/smoke checks:
  - airport-specific status renders in the intended consumer path
  - closures, delays, or ground-stop fields display without invented severity
  - missing-airport or unavailable branch behaves predictably
- Required export metadata checks:
  - export includes source id, raw airport code, updated time, fetched time, and caveats
  - export does not claim authoritative airport-wide state beyond FAA NAS scope
- Source health checks:
  - XML endpoint freshness is visible or documented
  - source-health wording does not imply airport matching certainty when reference matching is downstream
- Fixture/live mode checks:
  - XML fixture remains the deterministic backend basis
  - manual live verification stays separate from automated tests
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_faa_nas_status_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - airport workflow renders correctly in the current consumer path
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and unavailable-state behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists
  - executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`

### `washington-vaac-advisories`

- Owner agent:
  - `Aerospace AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/aerospace/space/washington-vaac-advisories`
  - test `app/server/tests/test_washington_vaac_contracts.py`
  - fixtures `app/server/data/washington_vaac_advisories_fixture.json` and `app/server/data/washington_vaac_advisories_empty_fixture.json`
  - client/export consumer coverage now exists through `aerospaceVaacContext.ts`, inspector wiring, export metadata, and smoke-fixture support
  - aerospace docs now record the implemented source slice and its no-inference boundaries
  - backend contracts, compile, lint, and build are explicitly recorded as passing
- Missing workflow evidence:
  - executed smoke/manual workflow evidence
- Required UI/smoke checks:
  - one bounded consumer path renders advisory number, volcano or region context, issue timing, and caveat text
  - advisory status remains clearly contextual and does not imply route impact or aircraft exposure
  - empty branch remains intelligible
- Required export metadata checks:
  - export includes source id, source URL, advisory identifiers, advisory timing, volcano or region summary, and caveat text
  - export preserves advisory/contextual semantics only
- Source health checks:
  - fixture empty behavior and degraded source status remain visible where surfaced
  - unavailable or disabled wording stays distinct from empty results
- Fixture/live mode checks:
  - fixtures remain deterministic and aligned with `test_washington_vaac_contracts.py`
  - any live-mode verification stays manual and bounded to the documented NOAA OSPO listing plus advisory XML path
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_washington_vaac_contracts.py -q`
  - `cmd /c npm.cmd run lint`
  - `cmd /c npm.cmd run build`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`

### `anchorage-vaac-advisories`

- Owner agent:
  - `Aerospace AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/aerospace/space/anchorage-vaac-advisories`
  - test `app/server/tests/test_anchorage_vaac_contracts.py`
  - fixtures `app/server/data/anchorage_vaac_advisories_fixture.json` and `app/server/data/anchorage_vaac_advisories_empty_fixture.json`
  - client/export consumer coverage now exists through `useAnchorageVaacAdvisoriesQuery`, `aerospaceVaacContext.ts`, inspector wiring, export metadata, and smoke-fixture support
  - backend contracts, compile, lint, and build are explicitly recorded as passing
- Missing workflow evidence:
  - executed smoke/manual workflow evidence
- Required UI/smoke checks:
  - one bounded consumer path renders advisory number, volcano or region context, issue timing, and caveat text
  - advisory status remains clearly contextual and does not imply route impact or aircraft exposure
  - empty branch remains intelligible
- Required export metadata checks:
  - export includes source id, source URL, advisory identifiers, advisory timing, volcano or region summary, and caveat text
  - export preserves advisory/contextual semantics only
- Source health checks:
  - fixture empty behavior and degraded source status remain visible where surfaced
  - unavailable or disabled wording stays distinct from empty results
- Fixture/live mode checks:
  - fixtures remain deterministic and aligned with `test_anchorage_vaac_contracts.py`
  - any live-mode verification stays manual and bounded to the documented advisory text-product path
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_anchorage_vaac_contracts.py -q`
  - `cmd /c npm.cmd run lint`
  - `cmd /c npm.cmd run build`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`

### `tokyo-vaac-advisories`

- Owner agent:
  - `Aerospace AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/aerospace/space/tokyo-vaac-advisories`
  - test `app/server/tests/test_tokyo_vaac_contracts.py`
  - fixtures `app/server/data/tokyo_vaac_advisories_fixture.json` and `app/server/data/tokyo_vaac_advisories_empty_fixture.json`
  - client/export consumer coverage now exists through `useTokyoVaacAdvisoriesQuery`, `aerospaceVaacContext.ts`, inspector wiring, export metadata, and smoke-fixture support
  - backend contracts, compile, lint, and build are explicitly recorded as passing
- Missing workflow evidence:
  - executed smoke/manual workflow evidence
- Required UI/smoke checks:
  - one bounded consumer path renders advisory number, volcano or region context, issue timing, and caveat text
  - advisory status remains clearly contextual and does not imply route impact or aircraft exposure
  - empty branch remains intelligible
- Required export metadata checks:
  - export includes source id, source URL, advisory identifiers, advisory timing, volcano or region summary, and caveat text
  - export preserves advisory/contextual semantics only
- Source health checks:
  - fixture empty behavior and degraded source status remain visible where surfaced
  - unavailable or disabled wording stays distinct from empty results
- Fixture/live mode checks:
  - fixtures remain deterministic and aligned with `test_tokyo_vaac_contracts.py`
  - any live-mode verification stays manual and bounded to the documented advisory text-product path
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_tokyo_vaac_contracts.py -q`
  - `cmd /c npm.cmd run lint`
  - `cmd /c npm.cmd run build`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and empty/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`

### `noaa-ndbc-realtime`

- Owner agent:
  - `Marine AI`
- Current validation level:
  - `workflow-validated`
- Existing evidence:
  - route `/api/marine/context/ndbc`
  - test `app/server/tests/test_marine_contracts.py`
  - fixture-backed marine context in `app/server/tests/smoke_fixture_app.py`
  - client hook `useMarineNdbcContextQuery`
  - downstream marine summary/export usage noted in repo evidence
  - explicit contract guarantees in [marine-context-source-contract-matrix.md](/C:/Users/mike/11Writer/app/docs/marine-context-source-contract-matrix.md:1)
  - explicit workflow evidence in [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1)
  - NDBC observations preserve `observed` evidence basis semantics
- Missing workflow evidence:
  - remaining gap is full-validation confirmation for `unavailable` or `degraded` source-health behavior and any live-mode caveat handling
- Required UI/smoke checks:
  - marine context path renders buoy observations and station metadata
  - unavailable station/file-family cases do not imply global outage
  - observation timestamps remain visible or inferable
- Required export metadata checks:
  - export includes source id, station id, observed time, fetched time, units, and caveats
  - export does not imply full archival completeness from realtime files
- Source health checks:
  - empty and disabled contract behavior is already covered at the backend contract layer
  - metadata and realtime observation health are not conflated if separately surfaced
  - stale buoy data is represented clearly
- Fixture/live mode checks:
  - marine contracts test remains the authoritative contract path
  - fixture mode is explicit in current contract coverage, including empty responses
  - smoke fixture app path should demonstrate deterministic NDBC context
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - marine contract tests pass
  - marine UI or evidence consumer shows NDBC fields correctly
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - stale-state wording and source-health behavior are explicitly validated
  - fixture path and live-mode caveats are documented together
  - `unavailable` or `degraded` behavior confirmation and live-mode assumption confirmation are explicitly recorded
- Known blockers:
  - no blocker for workflow-validated status
  - remaining work is only for any promotion beyond workflow-validated

### `scottish-water-overflows`

- Owner agent:
  - `Marine AI`
- Current validation level:
  - `workflow-validated`
- Existing evidence:
  - route `/api/marine/context/scottish-water-overflows`
  - test `app/server/tests/test_marine_contracts.py`
  - fixture-backed marine context in `app/server/tests/smoke_fixture_app.py`
  - client hook `useMarineScottishWaterOverflowsQuery`
  - downstream marine summary/export usage noted in repo evidence
  - explicit contract guarantees in [marine-context-source-contract-matrix.md](/C:/Users/mike/11Writer/app/docs/marine-context-source-contract-matrix.md:1)
  - explicit workflow evidence in [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1)
  - Scottish Water overflow events preserve `source-reported` evidence basis semantics
- Missing workflow evidence:
  - remaining gap is full-validation confirmation for `unavailable` or `degraded` source-health behavior and any live-mode caveat handling
- Required UI/smoke checks:
  - marine context path renders nearby overflow monitor status records
  - active, inactive, and unknown monitor states remain intelligible
  - empty or unavailable branch does not imply confirmed pollution impact
- Required export metadata checks:
  - export includes source id, monitor or event identifier when available, fetched time, source-generated time when available, and caveats
  - export preserves source-reported infrastructure semantics and does not imply contamination confirmation
- Source health checks:
  - empty and disabled contract behavior is already covered at the backend contract layer
  - source-health wording should distinguish empty nearby results from unavailable source state
  - stale event timing or generated-time wording should remain bounded
- Fixture/live mode checks:
  - marine contracts test remains the authoritative contract path
  - fixture mode is explicit in current contract coverage, including empty responses
  - smoke fixture app path should demonstrate deterministic Scottish Water context
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - marine contract tests pass
  - marine UI or evidence consumer shows Scottish Water fields correctly
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording for inactive, empty, stale, and unavailable cases is explicitly validated
  - fixture path and live-mode caveats are documented together
  - `unavailable` or `degraded` behavior confirmation and live-mode assumption confirmation are explicitly recorded
- Known blockers:
  - no blocker for workflow-validated status
  - remaining work is only for any promotion beyond workflow-validated

### `noaa-tsunami-alerts`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/events/tsunami/recent`
  - test `app/server/tests/test_tsunami_events.py`
  - fixture `app/server/data/noaa_tsunami_alerts_fixture.json`
  - client hook `useTsunamiAlertsQuery`
  - layer, entities, inspector, and app-shell consumption noted in repo evidence
- Missing workflow evidence:
  - explicit layer/inspector validation note
  - explicit export metadata validation note
- Required UI/smoke checks:
  - tsunami events appear in the intended layer or event workflow
  - selecting an event shows the expected detail path
  - Atom/CAP caveats remain visible and do not overstate impact area
- Required export metadata checks:
  - export includes source id, event identifier, observed/published time, fetched time, and caveats
  - export preserves warning/advisory wording instead of derived impact claims
- Source health checks:
  - feed freshness is visible or documented
  - unavailable feed state does not imply no tsunami activity
- Fixture/live mode checks:
  - fixture matches current test expectations
  - live Atom/CAP checks remain manual validation only
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_tsunami_events.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - layer and detail workflow are exercised successfully
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and stale/unavailable behavior are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists

### `uk-ea-flood-monitoring`

- Owner agent:
  - `Geospatial AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/events/uk-floods/recent`
  - test `app/server/tests/test_uk_ea_flood_events.py`
  - fixture `app/server/data/uk_ea_flood_monitoring_fixture.json`
  - client hook `useUkEaFloodMonitoringQuery`
  - layer and overview integration noted in repo evidence
- Missing workflow evidence:
  - explicit map/overview/inspector validation note
  - explicit export metadata validation note
- Required UI/smoke checks:
  - warnings/alerts appear in the target map or event workflow
  - selecting an item shows clear distinction between alert messaging and observation context
  - no-data or unavailable branch is intelligible
- Required export metadata checks:
  - export includes source id, alert id or station id, observed time where relevant, fetched time, and caveats
  - export does not merge warning and station observation semantics into one score
- Source health checks:
  - warning endpoint and reading endpoint health are separated if both appear
  - stale observations are labeled as such
- Fixture/live mode checks:
  - fixture remains deterministic and aligned with contract tests
  - manual live endpoint checks are documented separately
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_uk_ea_flood_events.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - layer or overview consumer path is exercised successfully
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health behavior and stale observation handling are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - implementation evidence is strong, but no explicit workflow-validation record exists

### `finland-digitraffic`

- Owner agent:
  - `Features/Webcam AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - list route `/api/features/finland-road-weather/stations`
  - detail route `/api/features/finland-road-weather/stations/{station_id}`
  - test `app/server/tests/test_finland_digitraffic.py`
  - fixtures `app/server/data/digitraffic_weather_stations_fixture.json` and `app/server/data/digitraffic_weather_station_data_fixture.json`
  - Features/Webcam AI progress records endpoint health, single-station detail, and freshness interpretation coverage
- Missing workflow evidence:
  - explicit consumer-path validation note
  - explicit export metadata validation note
  - explicit frontend rendering or feature-ops workflow evidence
- Required UI/smoke checks:
  - one bounded consumer path shows list and detail data without dropping freshness or endpoint-health semantics
  - sparse-coverage caveats remain distinct from source failure
  - no consumer path broadens the slice into cameras, rail, or marine domains
- Required export metadata checks:
  - export includes source id, station id, observed time, fetched time, endpoint-health or freshness interpretation when surfaced, and caveat text
  - export preserves observed-only semantics
- Source health checks:
  - metadata-endpoint and station-data-endpoint health remain distinct if both are shown
  - stale station readings remain distinct from sparse but current sensor coverage
- Fixture/live mode checks:
  - fixtures remain deterministic and aligned with `test_finland_digitraffic.py`
  - any live-mode verification stays bounded to the official road weather endpoints only
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_finland_digitraffic.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded consumer path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - endpoint-health, freshness, and sparse-coverage wording are explicitly validated
  - caveat language is confirmed in both UI and export
- Known blockers:
  - no explicit workflow-validation record exists yet

### `netherlands-rws-waterinfo`

- Owner agent:
  - `Marine AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/marine/context/netherlands-rws-waterinfo`
  - tests `app/server/tests/test_netherlands_rws_waterinfo.py` and `app/server/tests/test_marine_contracts.py`
  - pinned official POST endpoints for catalog metadata and latest water-level observations
  - fixtures and backend source-health handling for empty, disabled, stale, degraded, and unavailable behavior
  - marine docs now record the bounded WaterWebservices slice and its no-widening caveats
  - Marine AI progress now also records a completed bounded helper/export follow-on through `marineSourceHealthExportCoherence.ts` and `marineAnomalySummary.sourceHealthExportCoherence`
- Missing workflow evidence:
  - explicit recorded workflow validation over the completed helper/export path or an equivalent marine-local consumer path
  - explicit export metadata validation note
  - explicit UI or operational workflow evidence
- Required UI/smoke checks:
  - one bounded marine consumer or helper path shows station metadata and latest water-level observations without inventing impact semantics
  - partial metadata remains intelligible and inert
  - empty or unavailable branches remain distinct from normal observed results
- Required export metadata checks:
  - export includes source id, station id, water body if present, observed time, fetched time, units if present, source mode, source health, and caveats
  - export preserves observed-context semantics and does not imply hydrologic impact
- Source health checks:
  - `empty`, `disabled`, `stale`, `degraded`, and `unavailable` behavior remain distinct where surfaced
  - metadata-endpoint and latest-observation behavior are not conflated if both are described
- Fixture/live mode checks:
  - fixtures remain deterministic and aligned with `test_netherlands_rws_waterinfo.py`
  - any live-mode verification stays bounded to the approved WaterWebservices POST endpoints only
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_netherlands_rws_waterinfo.py -q`
  - `python -m pytest app/server/tests/test_marine_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - one bounded marine consumer or the completed helper/export path is exercised successfully
  - export metadata is checked and recorded once
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and partial-metadata behavior are explicitly validated
  - caveat language is confirmed in both UI/helper and export paths
- Known blockers:
  - no explicit workflow-validation record exists yet

### `nasa-jpl-cneos`

- Owner agent:
  - `Aerospace AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/aerospace/space/cneos-events`
  - test `app/server/tests/test_cneos_contracts.py`
  - fixture `app/server/data/cneos_space_context_fixture.json`
  - client hook `useCneosEventsQuery`
  - backend and hook evidence are clear; aerospace workflow docs now also record `cneosSpaceContext` plus `aerospaceContextIssues`
  - backend contracts, compile, lint, and build are explicitly recorded as passing
- Missing workflow evidence:
  - explicit consumer-path validation for close-approach and fireball records
  - explicit export metadata validation
  - explicit confirmation of current minimal UI presence
- Required UI/smoke checks:
  - current consumer path shows CNEOS records without inventing local threat scores
  - close approaches and fireballs remain distinct evidence classes
  - missing data branch is intelligible
- Required export metadata checks:
  - export includes source id, record type, object or event identifier, event time, fetched time, and caveats
  - export preserves derived-vs-observed distinctions where relevant
- Source health checks:
  - CAD and fireball endpoint freshness are treated independently if both are surfaced
  - source-health wording does not imply public-safety certainty
- Fixture/live mode checks:
  - fixture remains the deterministic basis for contract tests
  - manual live API checks are documented separately from automated verification
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_cneos_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - current UI or operational consumer path is exercised successfully
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and evidence-class separation are explicitly validated
  - UI and export caveats are confirmed together
- Known blockers:
  - current UI/export integration is better documented, but executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`

### `noaa-swpc-space-weather`

- Owner agent:
  - `Aerospace AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/aerospace/space/swpc-context`
  - test `app/server/tests/test_swpc_contracts.py`
  - fixture-backed context in `app/server/tests/smoke_fixture_app.py`
  - client hook `useSwpcSpaceWeatherContextQuery`
  - aerospace workflow docs record `swpcSpaceWeatherContext` plus `aerospaceContextIssues`
  - backend contracts, compile, lint, and build are explicitly recorded as passing
- Missing workflow evidence:
  - executed browser smoke for the current consumer path
  - explicit export metadata validation note beyond checklist presence
- Required UI/smoke checks:
  - current consumer path shows SWPC summary/advisory context without implying actual system failure
  - empty or unavailable branch is intelligible
  - source-health wording remains advisory/contextual only
- Required export metadata checks:
  - export includes source id, advisory context, fetched time, and caveat text
  - export preserves non-failure-overclaim semantics
- Source health checks:
  - freshness and advisory timing are visible when surfaced
  - unavailable and empty states remain distinct
- Fixture/live mode checks:
  - deterministic smoke fixture remains the authoritative contract basis
  - live validation stays separate from automated tests
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_swpc_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - current UI or operational consumer path is exercised successfully
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and caveat survival are explicitly validated
  - fixture/live-mode assumptions are documented together
- Known blockers:
  - executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`

### `noaa-ncei-space-weather-portal`

- Owner agent:
  - `Aerospace AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/aerospace/space/ncei-space-weather-archive`
  - test `app/server/tests/test_ncei_space_weather_portal_contracts.py`
  - fixture `app/server/data/ncei_space_weather_portal_fixture.xml`
  - client hook `useNceiSpaceWeatherArchiveQuery`
  - aerospace workflow docs record the bounded archive/context consumer path and export expectations
  - backend contracts, compile, lint, and build are explicitly recorded as passing
- Missing workflow evidence:
  - executed browser smoke for the current archive/context consumer path
  - explicit export metadata validation note beyond checklist presence
- Required UI/smoke checks:
  - current consumer path shows bounded archival space-weather metadata without merging it into current SWPC advisory truth
  - empty or unavailable branch is intelligible
  - free-text title and summary content remains inert source text
- Required export metadata checks:
  - export includes source id, archive item identifiers, source/generated time when present, fetched time, and caveat text
  - export preserves archival/context semantics only
- Source health checks:
  - archive feed freshness and empty results remain distinct from current-advisory availability
  - source-health wording does not imply live operational weather coverage
- Fixture/live mode checks:
  - deterministic XML fixture remains the authoritative contract basis
  - live validation stays separate from automated tests
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_ncei_space_weather_portal_contracts.py -q`
  - `cmd /c npm.cmd run lint`
  - `cmd /c npm.cmd run build`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - current UI or operational consumer path is exercised successfully
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and caveat survival are explicitly validated
  - fixture/live-mode assumptions are documented together
- Known blockers:
  - executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`

### `opensky-anonymous-states`

- Owner agent:
  - `Aerospace AI`
- Current validation level:
  - `implemented`
- Existing evidence:
  - route `/api/aerospace/aircraft/opensky/states`
  - test `app/server/tests/test_opensky_contracts.py`
  - fixture-backed context in `app/server/tests/smoke_fixture_app.py`
  - client hook `useOpenSkyStatesQuery`
  - aerospace workflow docs record `openskyAnonymousContext`, `openskyAnonymousContext.selectedTargetComparison`, and `aerospaceContextIssues`
  - backend contracts, compile, lint, and build are explicitly recorded as passing
- Missing workflow evidence:
  - executed browser smoke for the current consumer path
  - explicit export metadata validation note beyond checklist presence
- Required UI/smoke checks:
  - current consumer path shows source mode, health, comparison state, and caveat text
  - anonymous/rate-limited/non-authoritative caveats remain visible
  - no match and unavailable states remain distinct
- Required export metadata checks:
  - export includes source id, source mode, source health, aircraft count when applicable, selected-target comparison, fetched time, and caveat text
  - export preserves non-authoritative and non-replacement semantics
- Source health checks:
  - rate-limited, empty, degraded, and unavailable cases remain distinct when surfaced
  - comparison-state wording stays guarded and contextual
- Fixture/live mode checks:
  - deterministic smoke fixture remains the authoritative contract basis
  - live validation stays separate from automated tests
- Exact validation commands to run:
  - `python -m pytest app/server/tests/test_opensky_contracts.py -q`
- Pass criteria for `workflow-validated`:
  - contract tests pass
  - current UI or operational consumer path is exercised successfully
  - export metadata is checked and recorded
- Pass criteria for `fully validated`:
  - `workflow-validated` criteria pass
  - source-health wording and caveat survival are explicitly validated
  - fixture/live-mode assumptions are documented together
- Known blockers:
  - executed browser smoke is still missing on this host because Playwright launch is blocked by `windows-browser-launch-permission`

## Recommended Validation Order

1. `usgs-volcano-hazards`
2. `taiwan-cwa-aws-opendata`
3. `nrc-event-notifications`
4. `bmkg-earthquakes`
5. `ga-recent-earthquakes`
6. `noaa-tsunami-alerts`
7. `uk-ea-flood-monitoring`
8. `noaa-coops-tides-currents`
9. `noaa-ndbc-realtime`
10. `usgs-geomagnetism`
11. `natural-earth-physical`
12. `noaa-global-volcano-locations`
13. `nist-nvd-cve`
14. `noaa-aviation-weather-center-data-api`
15. `faa-nas-airport-status`
16. `washington-vaac-advisories`
17. `anchorage-vaac-advisories`
18. `tokyo-vaac-advisories`
19. `nasa-jpl-cneos`
20. `noaa-swpc-space-weather`
21. `noaa-ncei-space-weather-portal`
22. `opensky-anonymous-states`
23. `finland-digitraffic`

Rationale:

- start with geospatial event and context layers that can gain a first consumer fastest
- validate marine context pair together because they share contract tests and smoke-fixture structure
- validate new backend-first static/reference and CVE-context slices only after one bounded consumer or export path exists
- validate backend-first geospatial and features slices once they gain a first stable consumer path
- validate the three-VAAC package together because the bounded consumer/export wiring is shared
- validate aerospace context sources after marine because their export and workflow evidence is stronger now, but executed browser smoke is still launcher-blocked on this host
