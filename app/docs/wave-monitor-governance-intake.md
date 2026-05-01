# Wave Monitor Governance Intake

This packet is the current governance and ownership intake surface for Wave Monitor.

Use it with:

- [7po8-integration-plan.md](/C:/Users/mike/11Writer/app/docs/7po8-integration-plan.md)
- [unified-user-workflows.md](/C:/Users/mike/11Writer/app/docs/unified-user-workflows.md)
- [release-readiness.md](/C:/Users/mike/11Writer/app/docs/release-readiness.md)

Wave Monitor status in current repo evidence:

- implemented as a persistent backend tool surface with fixture-backed seed data
- integrated into shared analyst/readiness surfaces
- not workflow-validated
- not a separate mounted runtime
- not a new source of truth
- now also integrated with shared source-discovery memory seeding

Atlas implementation evidence matters here, but Atlas remains user-directed project input rather than Manager-controlled ownership.

## Current Implemented Slice

Current route:

- `GET /api/tools/waves/overview`
- `POST /api/tools/waves/{monitor_id}/run-now`
- `POST /api/tools/waves/scheduler/tick`

Shared-system integration already present:

- `GET /api/analyst/evidence-timeline`
  - includes `tool-wave-monitor` items when `include_wave_monitor=true`
- `GET /api/analyst/source-readiness`
  - includes a `tool-wave-monitor` readiness card
- `GET /api/source-discovery/memory/overview`
- `POST /api/source-discovery/memory/candidates`
- `POST /api/source-discovery/memory/claim-outcomes`

Current repo evidence:

- `app/server/src/types/wave_monitor.py`
- `app/server/src/services/wave_monitor_service.py`
- `app/server/src/routes/wave_monitor.py`
- `app/server/src/wave_monitor/db.py`
- `app/server/src/wave_monitor/models.py`
- `app/server/tests/test_wave_monitor.py`
- `app/server/src/routes/analyst.py`
- `app/server/src/services/analyst_workbench_service.py`
- `app/server/tests/test_analyst_workbench.py`
- `app/server/src/routes/source_discovery.py`
- `app/server/src/services/source_discovery_service.py`
- `app/server/src/types/source_discovery.py`
- `app/server/src/source_discovery/db.py`
- `app/server/src/source_discovery/models.py`
- `app/server/tests/test_source_discovery_memory.py`

Validation evidence recorded by Atlas:

- `python -m pytest app/server/tests/test_wave_monitor.py app/server/tests/test_analyst_workbench.py -q`
- `python -m compileall app/server/src`

## Fixture Status

Current status:

- persistent SQLite-backed Wave Monitor database is implemented
- persistent SQLite-backed source-discovery memory is implemented
- fixture-backed seed monitors and records are still the default bootstrap posture
- live connector execution exists only behind explicit API-triggered runs for connector rows marked `source_mode=live`
- manual scheduler tick exists only behind explicit API-triggered runs
- no autonomous background scheduler
- no frontend Situation Workspace panel

Interpretation:

- the tool surface is real and implemented
- persistent execution history and manual scheduler behavior are now implemented proof
- autonomous or hidden runtime behavior is still not implemented proof

## Evidence Basis

Wave Monitor is a tool and review surface, not a source family.

Its outputs should be treated as:

- tool-generated review context
- fixture-backed monitor summary context
- source-candidate and run-summary context
- safe hypothesis-review context where explicitly labeled

Wave Monitor outputs must not be treated as:

- direct event truth
- source authority
- legal conclusion
- autonomous action recommendation
- confirmation that a monitored topic is true, harmful, coordinated, or urgent

## Source Mode And Health Expectations

Current safe expectation:

- `sourceMode`
  - fixture-backed by default for the seeded overview slice
  - may be `live` for explicit connector rows configured with public feed URLs
- `sourceHealth`
  - tool/readiness accounting only for the current slice
  - not proof that live underlying sources are comprehensive, trustworthy, or currently available without explicit validation evidence

Readiness rule:

- a Wave Monitor readiness card or signal can explain review availability, fixture posture, or tool integration state
- it must not be read as live-source availability proof unless later implementation and validation explicitly add that evidence

## Caveats

Wave Monitor caveats must stay explicit:

- it is a tool surface, not source truth
- it is not a mounted standalone 7Po8 runtime
- it is not an autonomous scheduler or action engine
- manual API-triggered run-now and scheduler tick are not the same thing as approved background monitoring
- it may surface signals, source candidates, and monitor context, but those remain review inputs
- source-discovery memory and claim outcomes are reputation/accounting scaffolds, not source approval proof
- safe hypothesis-review language does not prove attribution, coordination, intent, causation, or wrongdoing

## Export Metadata Expectations

Any Wave Monitor export or shared metadata surface should preserve:

- tool label `Wave Monitor`
- route or surface identifier
- persistent storage posture
- whether the current monitor/connector slice is fixture-seeded, manually triggered, or both
- signal count / monitor count / source-candidate count where available
- source-health or readiness caveat line
- available actions as review actions only
- source-provenance and tool-caveat lines

Export must not:

- imply autonomous scheduling is live when it is not
- imply that source-memory or claim-outcome writes automatically promote, trust-score, validate, or schedule sources
- flatten tool context into event certainty
- turn monitor signals into action recommendations
- hide fixture-backed posture

## Owner Candidates

### `connect`

Best candidate for:

- shared route/service/test ownership
- validation truth
- runtime-mode integration
- future persistence/scheduler scaffolding
- broad/shared analyst-workbench and tool-surface wiring

### `data`

Best candidate for:

- future connector/feed-family semantics if Data AI feed registry becomes the first bounded Wave Monitor source set
- source-candidate policy for public information feeds routed through Wave Monitor

### `ui-integration`

Best candidate later for:

- workspace cards
- queue surfaces
- monitor drawers
- export preview polish

Only after:

- shared contracts stabilize
- Connect-owned runtime/tool semantics are clearer

### `gather`

Owns:

- governance
- status truth
- routing guidance
- caveat and do-not-do policy

### `atlas`

Current role:

- important user-directed implementation input
- not Manager-controlled ownership

Atlas progress should inform governance and validation notes, but should not by itself assign stable product ownership.

## Recommended Routing

Recommended current routing:

- keep Wave Monitor broad/shared for now
- treat Connect as the best owner candidate for shared contract, runtime, and validation follow-on
- treat Data as the best owner candidate for future bounded connector/feed semantics inside Wave Monitor
- treat source-discovery/source-memory reputation semantics as shared architecture for now; do not force them into Connect or Data ownership just to reduce `unknown`
- treat UI Integration as later consumer/presentation ownership only
- keep Gather on governance/status only

## Do Not Do

Do not let Wave Monitor become:

- a separate runtime glued sideways onto 11Writer
- an unreviewed autonomous scheduler/action engine
- an automatic source promoter, trust laundering path, or hidden live polling system
- a source-truth substitute
- a hidden autonomy claim beyond the current manual/persistent implementation
- a relationship or hypothesis engine that implies intent, wrongdoing, attribution, coordination, or action recommendation
- a source-approval shortcut that bypasses 11Writer source rules
