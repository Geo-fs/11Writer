# 11Writer Intelligence Loop

11Writer is a civilian, evidence-aware situational awareness platform. Its working loop is not just about loading sources. It is about keeping observation, context, caveats, and export discipline connected at every step.

## Loop Stages

### Observe

Observe is the intake layer.

- load public-source geospatial and environmental feeds
- load aerospace context feeds and flight or space-state context
- load marine replay, buoy, currents, and coastal-context inputs
- load webcam source inventories, lifecycle state, and source operations records
- load RSS and Atom discovery feeds as contextual leads
- load canonical reference and entity-linking context

Observe must also carry source health:

- loaded
- empty
- error
- stale or unknown when freshness cannot be established

### Orient

Orient is the context layer.

- place observations on the globe, timeline, inspector, and source summaries
- normalize records into source-aware entities and contracts
- keep observed records separate from derived summaries
- connect environmental, aerospace, marine, webcam, RSS, and reference context without claiming causation
- show whether a statement comes from a source field, a frontend helper, a ranking function, or a human-selected export scope

Orientation in 11Writer is deliberately evidence-scoped:

- proximity is not causation
- co-occurrence is not coordination
- source presence is not completeness
- missing data is a valid state and should stay visible

### Prioritize

Prioritize is the attention-management layer.

- rank marine anomalies without hiding the underlying evidence basis
- surface source health issues and ingestion gaps
- highlight recent or locally relevant environmental events
- summarize aerospace context around selected aircraft, airports, satellites, or space-weather state
- show webcam source lifecycle state, endpoint review results, and candidate-graduation context
- elevate RSS or media-search items only as discovery context, not as authoritative fact by themselves

Prioritization must always remain reviewable:

- what was observed
- what was inferred
- what was scored
- what caveats still apply

### Explain

Explain is the analyst-facing interpretation layer.

- generate source-aware summaries in the inspector and layer panels
- expose why an item was ranked, surfaced, or included
- preserve provenance in reference, environmental, marine, aerospace, webcam, and RSS-derived records
- distinguish source claims from local interpretation helpers
- keep uncertainty, freshness, and caveat lines visible

Explanation is a first-class product feature in 11Writer, not a post-processing step.

### Export

Export is the evidence-preservation layer.

- include source metadata and timestamps
- include selection context and snapshot metadata
- include source health where relevant
- include caveats needed to interpret the export later
- keep exports readable as analyst work products, not as unsupported claims of certainty

Exports should preserve enough context that another reviewer can tell:

- which source produced a record
- when it was observed
- whether freshness was known
- whether a statement was observed, derived, scored, or contextual

## Subsystem Mapping

### Geospatial and environmental sources

These support the full loop:

- Observe:
  - earthquakes
  - EONET
  - volcano status
  - tsunami alerts
  - UK flood monitoring
  - GeoNet
  - HKO weather
  - MET Norway alerts
  - Canada CAP
- Orient:
  - map layers
  - environmental overview helpers
  - selected-event summaries
- Prioritize:
  - recent-event visibility
  - nearest loaded event context
  - source-health awareness
- Explain:
  - source-aware inspector summaries
  - caveat lines for distance, recency, and mixed-source context
- Export:
  - environmental snapshot metadata and selected-event context

### Aerospace sources

- Observe:
  - OpenSky
  - FAA NAS status
  - aviation weather
  - SWPC
  - CNEOS and related space-context inputs
- Orient:
  - aircraft, airport, weather, and space-context helpers
- Prioritize:
  - selected-target operational context
  - data-health and availability summaries
- Explain:
  - aerospace context summaries and export profiles
- Export:
  - aerospace snapshot metadata and supporting source notes

### Marine context and anomaly workflows

- Observe:
  - replay tracks
  - CO-OPS and NDBC context
  - environmental and infrastructure context
  - Scottish Water overflow context where relevant
- Orient:
  - replay evidence
  - context timelines
  - issue queues
- Prioritize:
  - anomaly ranking
  - gap and context-source summaries
- Explain:
  - marine evidence summaries and interpretation helpers
- Export:
  - ranked anomaly metadata and supporting context state

### Webcam source operations

- Observe:
  - source inventory
  - endpoint evaluation
  - lifecycle status
  - candidate-graduation planning
- Orient:
  - operations panels
  - inventory summaries
  - source-health and readiness context
- Prioritize:
  - candidate review order
  - endpoint reliability issues
- Explain:
  - lifecycle summaries
  - evaluator and report outputs
- Export:
  - webcam source lifecycle metadata and operational review context

### RSS and Atom feeds

- Observe:
  - public or local-configured feed records through the generic parser
- Orient:
  - normalized title, link, item id, timestamps, categories, and feed metadata
- Prioritize:
  - discovery leads worth analyst review
- Explain:
  - source mode
  - freshness
  - discovery-only caveat
- Export:
  - feed metadata and caveat-preserving record summaries

RSS and Atom feeds in 11Writer are contextual discovery inputs. They are not automatically authoritative.

### Reference subsystem

- Observe:
  - canonical entity records and reviewed links
- Orient:
  - stable identifiers across multiple source families
- Prioritize:
  - which context should attach to which known entity
- Explain:
  - why a reference link is canonical, reviewed, or contextual
- Export:
  - reference-backed entity metadata and stable naming

### Export metadata

Export metadata spans the whole loop.

- preserve source names and timestamps
- preserve selected context
- preserve freshness and health where relevant
- preserve caveats
- preserve the difference between direct source record, local summary, and scored interpretation

## First-Class Platform Rules

In 11Writer, these are not optional polish items:

- source health is a feature
- evidence basis is a feature
- caveats are a feature
- provenance is a feature
- uncertainty visibility is a feature

The platform is strongest when it helps a user see what is known, what is missing, and why a conclusion should remain bounded.
