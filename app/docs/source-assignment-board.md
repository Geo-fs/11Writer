# Phase 2 Source Assignment Board

This board is the current truth for Phase 2 source status across the existing brief packs, prompt index, and ownership map.

Use it to answer:

- what is already implemented
- what is safe to assign next
- what still needs verification
- what should stay deferred
- how Gather should update status after agent reports

Related docs:

- [source-acceleration-phase2-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-briefs.md)
- [source-acceleration-phase2-international-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md)
- [source-acceleration-phase2-global-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md)
- [source-ownership-consumption-map.md](/C:/Users/mike/11Writer/app/docs/source-ownership-consumption-map.md)
- [source-prompt-index.md](/C:/Users/mike/11Writer/app/docs/source-prompt-index.md)

## Current Next Assignments

- Geospatial next: `geonet-geohazards` or `hko-open-weather`
- Marine next: maintain workflow-validated marine context sources and record any remaining stale/unavailable source-health checks before any promotion beyond `workflow-validated`
- Aerospace next: `nasa-jpl-cneos`
- Features/Webcam next: `finland-digitraffic` candidate prep
- Gather next: verify `eea-air-quality`, `singapore-nea-weather`, `esa-neocc-close-approaches`, and `imo-epos-geohazards`
- Connect next: repo-wide blocker fixing and release dry-run support

Status caution:

- Several sources below are `implemented` and clearly contract-tested in repo code.
- They are not `validated` unless workflow-level validation has been explicitly recorded.
- Treat `contract-tested` as stronger than `implemented`, but still weaker than `workflow-validated` or `validated`.
- `workflow-validated` here means fixture-backed contract, smoke, and export workflow evidence has been recorded.
- It does not mean fully validated, live validated, or upstream-source-live validated.

## Batch 3 Intake

Batch 3 statuses below are classification-only intake decisions from [source-acceleration-phase2-batch3-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch3-briefs.md). They do not imply code exists yet.

### Assignment-ready

| Source id | Owner agent | Consumer agents | Next action | Implementation priority | Notes |
| --- | --- | --- | --- | --- | --- |
| `metno-locationforecast` | `geospatial` | `marine`, `features-webcam`, `connect` | Assign a narrow backend-only point-forecast slice with controlled `User-Agent` headers. | `medium` | Ready only if production calls stay server-side or otherwise control `User-Agent`. |
| `metno-nowcast` | `geospatial` | `features-webcam`, `connect` | Assign one point nowcast slice with fixture-backed response handling. | `medium` | Treat as short-horizon forecast context, not observed weather. |
| `metno-metalerts-cap` | `geospatial` | `marine`, `features-webcam`, `connect` | Assign current alert feed parsing only. | `medium` | Keep alert semantics separate from forecast products. |
| `nve-flood-cap` | `geospatial` | `marine`, `connect` | Assign a flood-warning-only first slice from the public NVE forecast service. | `medium` | Do not mix with HydAPI or keyed NVE products. |
| `fmi-open-data-wfs` | `geospatial` | `marine`, `features-webcam`, `connect` | Assign one stored-query family only. | `medium` | Respect documented rate limits and avoid WFS sprawl. |
| `opensky-anonymous-states` | `aerospace` | `reference`, `connect` | Assign bounded current-state vectors only. | `medium` | Anonymous access is heavily rate-limited and not authoritative. |
| `emsc-seismicportal-realtime` | `geospatial` | `marine`, `connect` | Assign a fixture-first stream adapter with buffered event outputs. | `medium` | No live-websocket test dependence. |
| `meteoalarm-atom-feeds` | `geospatial` | `marine`, `features-webcam`, `connect` | Assign one country feed only. | `medium` | Use as normalized warning context, not final national-source truth. |

### Needs-verification

| Source id | Owner agent | Next action | Notes |
| --- | --- | --- | --- |
| `nve-regobs-natural-hazards` | `geospatial` | Recheck the official read-only public API surface and pin a stable unauthenticated GET path. | Avoid drifting into documented OAuth2 or account-backed flows. |
| `npra-traffic-volume` | `features-webcam` | Pin a stable official machine endpoint before any assignment. | Official dataset pages were visible, but the direct production endpoint was not pinned cleanly enough. |
| `adsb-lol-aircraft` | `aerospace` | Recheck the current public API posture, limits, and stability before assignment. | Community/open aviation source with weaker authority and changing service expectations. |
| `sensor-community-air-quality` | `geospatial` | Verify the official stable machine-readable observation endpoint. | Community/volunteer data should be clearly labeled if approved later. |
| `safecast-radiation` | `geospatial` | Verify the production API path beyond generic download pages. | Community/volunteer source with evidence-language sensitivity. |

### Deferred

| Source id | Owner agent | Reason |
| --- | --- | --- |
| `airplanes-live-aircraft` | `aerospace` | Public access exists, but non-commercial/no-SLA posture makes it weak for current Phase 2 implementation. |
| `wmo-swic-cap-directory` | `geospatial` | Discovery directory only, not final event truth. |
| `cap-alert-hub-directory` | `geospatial` | Discovery directory only, not a direct event feed. |

### Duplicate

| Source id | Owner agent | Reason |
| --- | --- | --- |
| `nasa-gibs-ogc-layers` | `gather` | Current imagery stack already uses NASA GIBS WMTS, so a separate source track would duplicate existing coverage. |

### Rejected

| Source id | Owner agent | Reason |
| --- | --- | --- |
| `nve-hydapi` | `geospatial` | Official access requires an API key, which violates current no-signup/no-key rules. |
| `npra-datex-traffic` | `features-webcam` | Official access requires registration, which violates current no-signup rules. |
| `jma-public-weather-pages` | `geospatial` | Only public HTML pages were verified, not a stable machine-readable endpoint. |

## Source Status Lifecycle

### `idea`

- Meaning:
  - A source is only a possible future candidate and has not yet been vetted into the current Phase 2 brief flow.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - Source name and rough rationale only.
- Next allowed transitions:
  - `candidate`
  - `rejected`

### `candidate`

- Meaning:
  - A source has an official-looking path or provider family worth checking, but no stable assignment-ready brief yet.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - Official docs page or official provider landing page.
- Next allowed transitions:
  - `briefed`
  - `needs-verification`
  - `deferred`
  - `rejected`

### `briefed`

- Meaning:
  - Gather has written a connector brief or equivalent scoped handoff notes, but the source is not yet safe to assign without a final status call.
- Who can set it:
  - `Gather`
- Required evidence:
  - A source brief with owner recommendation, first slice, caveats, and validation commands.
- Next allowed transitions:
  - `assignment-ready`
  - `needs-verification`
  - `deferred`
  - `rejected`

### `assignment-ready`

- Meaning:
  - The source has a narrow enough first slice, clear owner, and safe no-auth posture to hand off now.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - Scoped brief
  - official docs URL
  - sample endpoint or verified machine path
  - owner recommendation
  - fixture-first plan
- Next allowed transitions:
  - `assigned`
  - `needs-verification`
  - `deferred`
  - `rejected`

### `assigned`

- Meaning:
  - A domain agent has been explicitly handed the source, but code-level progress is not yet confirmed.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - Clear assignment message or handoff prompt naming the owner agent.
- Next allowed transitions:
  - `in-progress`
  - `blocked`
  - `needs-verification`

### `in-progress`

- Meaning:
  - The owner agent has started real implementation work, or backend/service/test work exists but the end-to-end source slice is not yet complete.
- Who can set it:
  - `Gather`
  - owner agent reporting to `Gather`
  - `Connect`
- Required evidence:
  - At least one of:
    - backend route or service added
    - typed contracts added
    - tests or fixtures added
    - client hook or minimal UI started
- Next allowed transitions:
  - `implemented`
  - `blocked`
  - `needs-verification`
  - `rejected`

### `implemented`

- Meaning:
  - The first implementation slice exists in repo code with route/service/contracts/tests and enough client or operational integration to use it.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - fixture-first backend service
  - typed API contract
  - route
  - tests
  - client hook or minimal operational consumption
  - source-health/caveat fields preserved
- Next allowed transitions:
  - `workflow-validated`
  - `validated`
  - `blocked`
  - `needs-verification`

### `workflow-validated`

- Meaning:
  - The source is implemented and has explicit workflow evidence showing contract coverage plus operational consumer-path validation such as smoke and export metadata checks.
- Who can set it:
  - `Gather`
  - `Connect`
  - owner agent reporting explicit workflow evidence to `Gather`
- Required evidence:
  - implemented slice present
  - contract tests pass
  - deterministic smoke or documented workflow validation passes
  - export metadata or equivalent workflow output is checked when the source participates in export
- Next allowed transitions:
  - `validated`
  - `blocked`
  - `needs-verification`

### `validated`

- Meaning:
  - The source is implemented and confirmed usable in workflow with passing relevant validation.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - implemented slice present
  - relevant validation passed
  - source is usable in workflow, not only reachable in tests
- Next allowed transitions:
  - `blocked`
  - `needs-verification`

### `blocked`

- Meaning:
  - Work exists, but progress is currently blocked by a known issue.
- Who can set it:
  - `Gather`
  - owner agent
  - `Connect`
- Required evidence:
  - specific blocker note
  - blocked scope clearly named
- Next allowed transitions:
  - `in-progress`
  - `needs-verification`
  - `rejected`

### `needs-verification`

- Meaning:
  - Official docs or candidate endpoints exist, but the no-auth or machine-readable posture is still uncertain enough that assignment should pause.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - exact missing piece named, such as:
    - endpoint path not pinned
    - auth posture inconsistent
    - transport or certificate uncertainty
    - unclear public-machine endpoint
- Next allowed transitions:
  - `candidate`
  - `briefed`
  - `assignment-ready`
  - `rejected`

### `deferred`

- Meaning:
  - The source is official/public but still too broad, too operationally messy, or too low-leverage for the current Phase 2 flow.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - a clear reason that the source is not currently worth first-slice implementation
- Next allowed transitions:
  - `candidate`
  - `briefed`
  - `assignment-ready`
  - `rejected`

### `rejected`

- Meaning:
  - The source violates the no-auth/no-signup/no-CAPTCHA/public-machine-endpoint rules or otherwise should not be used.
- Who can set it:
  - `Gather`
  - `Connect`
- Required evidence:
  - explicit rule violation or unstable access posture
- Next allowed transitions:
  - none unless the provider access model materially changes and Gather reopens it as a new candidate

## How To Update This Board After Agent Reports

- If an agent adds backend route, contracts, fixtures, and tests but frontend integration is incomplete:
  - set status to `in-progress`
- If an agent adds fixture-backed backend work, tests, client integration or minimal UI, export metadata, and the relevant validation passes:
  - set status to `implemented`
- If a source is implemented and full relevant validation passes and the source is usable in workflow:
  - set status to `validated`
- If a source is blocked by repo-wide lint or build failures unrelated to the source itself:
  - keep status at `in-progress`
  - add a blocker note rather than downgrading the source
- If source access becomes uncertain or the official machine endpoint is no longer clear:
  - set or return the source to `needs-verification`
- If the source now requires login, signup, API key, email request, request-access flow, or CAPTCHA:
  - set status to `rejected`
- If an agent report only shows docs work or prompt preparation:
  - do not move beyond `briefed` or `assignment-ready`
- If an agent report only shows route stubs with no fixtures or tests:
  - do not move beyond `assigned` or `in-progress`

## Report Intake Template

Use this template when Gather processes a domain-agent source report:

```text
Source id:
Agent:
Files changed:
Backend added?:
Client added?:
Fixtures/tests added?:
UI added?:
Export metadata added?:
Validation passed?:
Blockers?:
Status update:
Next action:
```

## Implementation Completeness Checklist

- fixture-first backend service
- typed API contracts
- route
- tests
- client types or query hook
- source health
- minimal operational UI if needed
- export metadata
- docs
- no overclaim or caveat rules preserved
- no live-network tests

## Board

| Source id | Current status | Owner agent | Consumer agents | Brief doc link | Next action | Do-not-do warning | Implementation priority | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `usgs-volcano-hazards` | `implemented` | `geospatial` | `aerospace`, `features-webcam`, `connect` | [U.S. briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-briefs.md:10) | Keep source-health and export metadata stable; only promote to `validated` after current workflow validation is explicitly rerun and recorded | Do not claim ash dispersion or route impact from status alone | `high` | Repo evidence found: route, service, tests, client query, layer, inspector/app-shell consumption |
| `noaa-coops-tides-currents` | `workflow-validated` | `marine` | `geospatial`, `connect` | [U.S. briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-briefs.md:101) | Keep source semantics caveats intact and promote only to `validated` after broader full-validation/live-behavior evidence is explicitly recorded | Do not mix predictions with observations | `high` | Contract-covered, marine-smoke-covered, and export-metadata-covered per [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1); not fully validated/live validated |
| `noaa-aviation-weather-center-data-api` | `implemented` | `aerospace` | `reference`, `connect` | [U.S. briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-briefs.md:199) | Preserve bounded airport context and source health; promote to `validated` only after current end-to-end workflow validation is explicitly recorded | Do not pull broad worldwide result sets | `high` | Repo evidence found: route, adapter, service, contracts, tests, client hook, inspector/app-shell usage |
| `faa-nas-airport-status` | `implemented` | `aerospace` | `reference`, `connect` | [U.S. briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-briefs.md:304) | Keep airport-specific route and source status behavior stable; validate workflow before `validated` | Do not scrape the FAA NAS UI | `high` | Repo evidence found: dedicated route module, contracts tests, client hook, inspector/app-shell usage |
| `noaa-ndbc-realtime` | `workflow-validated` | `marine` | `geospatial`, `connect` | [U.S. briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-briefs.md:402) | Keep source semantics caveats intact and promote only to `validated` after broader full-validation/live-behavior evidence is explicitly recorded | Do not assume every station exposes every file family | `high` | Contract-covered, marine-smoke-covered, and export-metadata-covered per [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1); not fully validated/live validated |
| `noaa-tsunami-alerts` | `implemented` | `geospatial` | `marine`, `connect` | [Prompt index](/C:/Users/mike/11Writer/app/docs/source-prompt-index.md:432) | Keep Atom/CAP caveats stable and validate workflow before `validated` | Do not infer impact area beyond source messaging | `high` | Repo evidence found: route, tests, client query, layer, entities, inspector/app-shell consumption |
| `uk-ea-flood-monitoring` | `implemented` | `geospatial` | `marine`, `reference`, `connect` | [International briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md:10) | Preserve route/filter behavior and evidence separation; promote to `validated` only after workflow validation is explicitly recorded | Do not merge warnings and observations into one score | `high` | Repo evidence found: route, service, types, tests, client query, layer, overview integration |
| `geonet-geohazards` | `assignment-ready` | `geospatial` | `aerospace`, `connect` | [International briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md:147) | Assign NZ quake plus volcanic alert-level first slice | Do not flatten quake and volcano records into one severity scale | `high` | Strong next geospatial assignment candidate |
| `nasa-jpl-cneos` | `implemented` | `aerospace` | `geospatial`, `connect` | [International briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md:267) | Keep bounded event-type query and evidence-class separation stable; promote to `validated` only after workflow validation is explicitly recorded | Do not invent local threat scores | `high` | Repo evidence found: dedicated route module, tests, client hook; broader UI integration appears partial but the source slice itself is implemented |
| `canada-cap-alerts` | `assignment-ready` | `geospatial` | `marine`, `connect` | [International briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md:386) | Assign current CAP directory discovery plus bounded CAP XML parsing | Do not traverse the full archive by default | `medium` | Directory-oriented but still considered assignment-ready |
| `dwd-cap-alerts` | `assignment-ready` | `geospatial` | `connect` | [International briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md:504) | Assign one snapshot family, recommended `DISTRICT_DWD_STAT` | Do not mix snapshot and diff feeds | `medium` | Safe if kept to one family only |
| `finland-digitraffic` | `assignment-ready` | `features-webcam` | `geospatial`, `connect` | [International briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-international-briefs.md:620) | Start candidate prep or road-weather station first slice | Do not combine road weather with cameras, AIS, and rail in one patch | `medium` | First slice should stay roadside/weather station scoped |
| `eea-air-quality` | `needs-verification` | `geospatial` | `geospatial`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:31) | Pin one stable bounded observation endpoint or keep to station metadata only | Do not start with Europe-wide multi-pollutant harvesting | `medium` | Main gap is exact backend-safe time-series endpoint confirmation |
| `canada-geomet-ogc` | `assignment-ready` | `geospatial` | `geospatial`, `marine`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:122) | Assign one pinned collection only | Do not normalize the entire GeoMet catalog | `medium` | Collection-scoped implementation only |
| `dwd-open-weather` | `assignment-ready` | `geospatial` | `geospatial`, `marine`, `aerospace`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:205) | Assign one observation or forecast family only | Do not normalize the whole DWD tree | `medium` | Product-family scoping is the main constraint |
| `bom-anonymous-ftp` | `deferred` | `geospatial` | `geospatial`, `marine`, `aerospace`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:287) | Narrow to one explicitly approved product family before any code work | Do not treat the whole BoM catalog as one connector | `low` | Official/public but still too broad for a safe first connector |
| `hko-open-weather` | `assignment-ready` | `geospatial` | `geospatial`, `marine`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:343) | Assign `warningInfo` only | Do not assume all HKO datasets share one query model | `medium` | One of the cleanest global ready sources |
| `singapore-nea-weather` | `needs-verification` | `geospatial` | `geospatial`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:425) | Re-verify current no-auth posture, then pin PM2.5 plus one station family | Do not assume the entire family is uniformly keyless | `medium` | Endpoint behavior looked keyless, docs still mention key flows |
| `meteoswiss-open-data` | `assignment-ready` | `geospatial` | `geospatial`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:511) | Assign STAC collection plus one recent observation asset family | Do not attempt the full product catalog | `medium` | Narrow and well-scoped global weather candidate |
| `scottish-water-overflows` | `workflow-validated` | `marine` | `geospatial`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:593) | Keep overflow-status caveats intact and promote only to `validated` after broader full-validation/live-behavior evidence is explicitly recorded | Do not present activation as confirmed contamination | `medium` | Contract-covered, marine-smoke-covered, and export-metadata-covered per [marine-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/marine-workflow-validation.md:1); still contextual only and not fully validated/live validated |
| `esa-neocc-close-approaches` | `needs-verification` | `aerospace` | `aerospace`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:670) | Pin one exact raw-text endpoint from official docs before code work | Do not assume the experimental interface is stable | `medium` | Official docs exist, exact machine endpoint still not pinned |
| `imo-epos-geohazards` | `needs-verification` | `geospatial` | `geospatial`, `connect` | [Global briefs](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-global-briefs.md:749) | Verify one stable official machine endpoint or keep blocked | Do not implement from unofficial Iceland feeds | `low` | Official-path confirmation is still too weak for connector work |

## Status Buckets

### Workflow-Validated

- `noaa-coops-tides-currents`
- `noaa-ndbc-realtime`
- `scottish-water-overflows`

Current interpretation:

- these sources are implemented, contract-tested, smoke-covered, and export-metadata-covered
- they are not yet `validated` or `fully validated`
- they should not be treated as live validated from fixture-backed workflow evidence alone

### Implemented

- `usgs-volcano-hazards`
- `noaa-aviation-weather-center-data-api`
- `faa-nas-airport-status`
- `noaa-tsunami-alerts`
- `uk-ea-flood-monitoring`
- `nasa-jpl-cneos`

Current interpretation:

- these sources are implemented
- most are contract-tested
- none are promoted to `validated` by this board without explicit workflow-validation evidence

### In Progress

No additional sources are currently held in `in-progress` after the latest repo reconciliation pass.

If an owner lands partial work without the full first slice, Gather should reintroduce `in-progress` with a blocker or scope note.

### Assignment-Ready

- `geonet-geohazards`
- `canada-cap-alerts`
- `dwd-cap-alerts`
- `finland-digitraffic`
- `canada-geomet-ogc`
- `dwd-open-weather`
- `hko-open-weather`
- `meteoswiss-open-data`

### Needs-Verification

- `eea-air-quality`
- `singapore-nea-weather`
- `esa-neocc-close-approaches`
- `imo-epos-geohazards`

### Deferred

- `bom-anonymous-ftp`

### Blocked/Rejected

No sources from the requested board list are currently placed here.

Related registry-side rejected example outside this board scope:

- `iceland-earthquakes`

## Recommended Next Assignments

- Geospatial: `geonet-geohazards` or `hko-open-weather`
- Aerospace: `nasa-jpl-cneos` only if follow-on work is needed beyond the current implemented slice; otherwise next fresh assignment should stay elsewhere
- Marine: no fresh source handoff from this trio right now; preserve caveat/source-health quality on `noaa-coops-tides-currents`, `noaa-ndbc-realtime`, and `scottish-water-overflows`
- Features/Webcam: `finland-digitraffic` candidate prep
- Gather: verify `needs-verification` sources
- Connect: repo-wide blocker fixing and release dry-run support

## Recently Implemented / Started

Recently implemented or clearly code-present in the repo:

- USGS Volcano Hazards
  - Route, service, tests, query hook, and UI-layer consumption are present.
- NOAA Tsunami Alerts
  - Route, tests, query hook, and UI-layer consumption are present.
- NOAA CO-OPS
  - Marine context route, service, tests, query hook, export/evidence consumption, and workflow-validation evidence are present.
- NOAA NDBC
  - Marine context route, service, tests, query hook, export/evidence consumption, and workflow-validation evidence are present.
- Scottish Water Overflows
  - Marine context route, service, tests, query hook, export/evidence consumption, and workflow-validation evidence are present.
- NOAA AWC
  - Route, adapter, service, tests, query hook, and inspector/app-shell usage are present.
- FAA NAS
  - Dedicated route, contracts tests, query hook, and inspector/app-shell usage are present.

## Inconsistency Notes

Current planning docs are now closer to aligned, but a few notes remain:

- `faa-nas-airport-status`
  - Earlier prompt docs framed this as ready-to-assign.
  - Repo evidence now supports `implemented`, so the board has been promoted accordingly.
- `noaa-ndbc-realtime`
  - Earlier prompt docs framed this as ready-to-assign.
  - Repo evidence now supports `workflow-validated`, so the board has been promoted accordingly.
- `noaa-coops-tides-currents`
  - Earlier planning treated this as implemented/contract-tested only.
  - Marine workflow evidence now supports `workflow-validated`, but not `validated`.
- `scottish-water-overflows`
  - Earlier planning treated this as assignment-ready.
  - Marine workflow evidence now supports `workflow-validated`, but not `validated`.
- `noaa-tsunami-alerts`
  - Earlier planning treated it as started from registry and prompt readiness.
  - Repo evidence now supports `implemented`.
- `uk-ea-flood-monitoring`
  - Earlier planning treated it as assignment-ready.
  - Repo evidence now supports `implemented`.
- `nasa-jpl-cneos`
  - Earlier planning treated it as assignment-ready.
  - Repo evidence now supports `implemented` at the source-slice level, though additional UI follow-ons may still be useful.
- `validated`
  - This board does not promote any source to `validated` in this docs pass because Gather did not rerun the relevant validation suite here.
  - Promote from `implemented` to `validated` only when passing workflow-level validation is explicitly recorded.
