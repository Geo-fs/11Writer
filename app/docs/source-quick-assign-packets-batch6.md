# Source Quick-Assign Packets: Batch 6

Compact Phase 2 handoff packets for the strongest Batch 6 assignment-ready sources.

Use this doc when you want:

- a shorter handoff than the full Batch 6 brief pack
- an owner-correct copy-paste prompt
- Observe -> Orient -> Prioritize -> Explain -> Act framing in the first patch
- tight source-health, caveat, and export expectations

Status note:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md) remains the status truth.
- These packets are intentionally shorter than [source-acceleration-phase2-batch6-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md).
- [source-consolidated-noauth-registry.md](/C:/Users/mike/11Writer/app/docs/source-consolidated-noauth-registry.md) is backlog context only and does not promote implementation or validation status by itself.
- Runtime notes below must preserve one shared backend/core and must not imply companion-web exposure, remote binding, or broad CORS changes.

## Recommended Immediate Assignment Order

1. `geosphere-austria-warnings`
2. `washington-vaac-advisories`
3. `taiwan-cwa-aws-opendata`
4. `bart-gtfs-realtime`
5. `nasa-power-meteorology-solar`
6. `anchorage-vaac-advisories`
7. `nrc-event-notifications`

## 1. `geosphere-austria-warnings`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Goal:
  Add one bounded Austrian warning-context source so the environmental layer can ingest official warning records with source severity semantics intact, while keeping the output advisory/contextual and avoiding any impact or damage claims.
- First safe slice:
  Current warning feed only.
- Observe input:
  Official machine-readable Austrian warning records from one pinned public warning feed.
- Orient output:
  Normalized warning cards or event rows with source severity/color, warning type, area text, time windows, provenance, and advisory caveats.
- Evidence basis:
  `advisory`
- Source mode/health expectation:
  Fixture-first by default, with explicit `fixture`, `live`, `empty`, `disabled`, and `error` states if implemented later.
- Caveats:
  - warning color and text are advisory/contextual only
  - preserve source-native severity semantics
  - do not infer observed damage, closures, or causation
- Export metadata:
  - source id and source URL
  - fetched time
  - warning count
  - severity summary
  - advisory caveat summary
- Fusion-layer mapping:
  - Observe: warning feed records
  - Orient: normalized warning context by area and time window
  - Prioritize: severity and time-window filtering only
  - Explain: provenance plus caveat-preserving summary
  - Act: bounded alert awareness, not impact scoring
- Runtime/interface note:
  Shared backend/core only. Safe for desktop and backend-only runtime; do not imply companion-web exposure changes.
- Do-not-do list:
  - do not infer impact or damage from warning color alone
  - do not widen into a general Austrian weather platform
  - do not flatten source-native warning semantics into a fake global severity score
- Validation commands:
  - use the pinned endpoint and checks in [source-acceleration-phase2-batch6-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md)
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `geosphere-austria-warnings`.

Owner: Geospatial AI.

Goal:
- Add one bounded Austrian warning-context source using the official public warning feed.

Scope:
- Current warning feed only.
- Preserve source-native severity/color and warning-type semantics.
- No wider Austrian weather-platform expansion.

Observe -> Orient expectations:
- Observe: official warning feed records.
- Orient: normalized warning rows/cards with area text, time windows, severity/color, provenance, and advisory caveats.

Implementation requirements:
- Fixture-first only.
- Keep source mode, source health, provenance, and advisory caveats explicit.
- Export metadata must preserve source id, source URL, fetched time, warning count, severity summary, and advisory caveats.

Do not:
- infer impact, damage, or causation from warning color alone
- invent a global severity scale that erases source semantics
- broaden into forecasts, observations, or unrelated Austrian products
```

## 2. `washington-vaac-advisories`

- Recommended owner agent: `aerospace`
- Current status: `assignment-ready`
- Goal:
  Add one bounded volcanic-ash advisory context source so aerospace and geospatial consumers can use official Washington VAAC messaging without overstating plume precision, route impact, or ash-dispersion certainty.
- First safe slice:
  One volcanic ash advisory feed family only.
- Observe input:
  Official VAAC advisory text/feed records from Washington VAAC.
- Orient output:
  Normalized advisory context with volcano name, advisory time, region text, advisory status, source URL, and caveat-preserving ash-context summary.
- Evidence basis:
  `advisory`
- Source mode/health expectation:
  Fixture-first by default, with explicit source-mode and freshness fields preserved for later smoke or export checks.
- Caveats:
  - advisory ash context only
  - preserve source wording around observed versus forecast ash
  - do not claim route disruption, ash footprint, or dispersion precision beyond source messaging
- Export metadata:
  - source id and source URL
  - advisory identifiers
  - volcano or region summary
  - advisory issued/updated time
  - advisory-context caveats
- Fusion-layer mapping:
  - Observe: VAAC advisory records
  - Orient: ash advisory context tied to volcano/region and advisory timing
  - Prioritize: advisory recency and advisory-state filters only
  - Explain: advisory provenance and wording-preserving summary
  - Act: bounded operational awareness, not route-impact automation
- Runtime/interface note:
  Shared backend/core only. Safe for desktop and backend-only runtime; do not recommend exposure changes for remote/browser use.
- Do-not-do list:
  - do not claim ash dispersion precision beyond advisory text
  - do not convert advisory status into hard flight-impact claims
  - do not merge multiple VAAC feeds into one fake severity vocabulary in the first patch
- Validation commands:
  - use the pinned endpoint and checks in [source-acceleration-phase2-batch6-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md)
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `washington-vaac-advisories`.

Owner: Aerospace AI.

Goal:
- Add one bounded Washington VAAC advisory-context source for volcanic ash awareness.

Scope:
- One advisory feed family only.
- Preserve source wording around advisory state, volcano/region, and timing.
- No ash-dispersion modeling, no route-impact scoring, and no multi-VAAC fusion framework.

Observe -> Orient expectations:
- Observe: official VAAC advisory records.
- Orient: normalized advisory context with volcano/region text, advisory timing, provenance, and advisory caveats.

Implementation requirements:
- Fixture-first only.
- Keep source mode, source health, provenance, and advisory caveats explicit.
- Export metadata must preserve source id, source URL, advisory identifiers, advisory time, volcano/region summary, and caveat text.

Do not:
- claim ash dispersion precision beyond advisory text
- invent route impact from advisory presence alone
- flatten VAAC-specific semantics into a global severity score
```

## 3. `taiwan-cwa-aws-opendata`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Goal:
  Add one bounded Taiwan public-bucket weather or warning context source that stays inside clearly public AWS-backed files and does not drift into key-gated CWA APIs or broad catalog ingestion.
- First safe slice:
  One public AWS-backed warning or weather file family only.
- Observe input:
  One pinned public CWA AWS-backed file family with stable machine-readable records.
- Orient output:
  Normalized warning-context or weather-context records with provenance, record time, area or station labels, and explicit caveats about the chosen file family.
- Evidence basis:
  `advisory` for warnings or `observed` for station/weather observations, depending on the chosen first slice
- Source mode/health expectation:
  Fixture-first by default, with explicit source mode and freshness fields that distinguish file fetch time from event/observation time.
- Caveats:
  - stay inside clearly public AWS-backed files only
  - preserve whether the slice is warning/advisory or observed/weather context
  - do not imply access to the wider key-gated CWA product families
- Export metadata:
  - source id and source URL
  - chosen file-family identifier
  - fetched time
  - record count
  - advisory or observed caveat summary
- Fusion-layer mapping:
  - Observe: one public AWS-backed file family
  - Orient: normalized warning or weather-context records
  - Prioritize: bounded record filtering by time or type only
  - Explain: provenance-preserving context summary
  - Act: contextual awareness, not unsupported operational claims
- Runtime/interface note:
  Shared backend/core only. Safe for desktop and backend-only runtime; do not suggest remote-access changes.
- Do-not-do list:
  - do not drift into key-gated CWA APIs
  - do not mix warning/advisory semantics with observed-weather semantics without explicit labeling
  - do not broaden into multiple CWA product families in the first patch
- Validation commands:
  - use the pinned endpoint and checks in [source-acceleration-phase2-batch6-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md)
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `taiwan-cwa-aws-opendata`.

Owner: Geospatial AI.

Goal:
- Add one bounded Taiwan public-bucket weather or warning context source using only clearly public AWS-backed files.

Scope:
- One public AWS-backed file family only.
- Preserve whether the slice is advisory or observed context.
- No drift into key-gated CWA APIs and no broad multi-product ingestion.

Observe -> Orient expectations:
- Observe: one pinned public AWS-backed file family.
- Orient: normalized records with provenance, timing, area or station labels, and explicit caveats.

Implementation requirements:
- Fixture-first only.
- Keep source mode, source health, fetched time, record time, provenance, and caveats explicit.
- Export metadata must preserve source id, source URL, file-family identifier, fetched time, record count, and evidence-basis caveats.

Do not:
- use key-gated normal CWA APIs
- merge advisory and observed semantics without explicit labels
- broaden into multiple Taiwan weather product families in the first patch
```

## 4. `bart-gtfs-realtime`

- Recommended owner agent: `features-webcam`
- Current status: `assignment-ready`
- Goal:
  Add one bounded BART realtime operational-context source so the features/webcam lane can consume a single public transit feed without widening into a full transit analytics platform or inventing service-impact semantics beyond the chosen feed.
- First safe slice:
  One vehicle-position, trip-update, or alert feed only.
- Observe input:
  One pinned public BART GTFS-realtime feed family.
- Orient output:
  Normalized operational-context records for the chosen feed family with provenance, freshness, feed-family labels, and limited service-context caveats.
- Evidence basis:
  `source-reported`
- Source mode/health expectation:
  Fixture-first by default, with explicit source-mode and freshness expectations because realtime feeds can go stale or sparse.
- Caveats:
  - one feed family only
  - preserve feed-family semantics
  - do not infer network-wide disruption from a sparse realtime sample
- Export metadata:
  - source id and source URL
  - feed family
  - fetched time
  - freshness summary
  - service-context caveats
- Fusion-layer mapping:
  - Observe: one realtime transit feed family
  - Orient: normalized operational context for vehicles, trips, or alerts
  - Prioritize: freshness and bounded service-status filters only
  - Explain: provenance and caveat-preserving operational summary
  - Act: bounded operator awareness, not transit-platform sprawl
- Runtime/interface note:
  Shared backend/core only. Safe for desktop and backend-only runtime; do not imply external companion access or remote polling changes.
- Do-not-do list:
  - do not widen into a full transit analytics platform
  - do not merge all GTFS-realtime feed families in the first patch
  - do not invent outage or rider-impact claims beyond source records
- Validation commands:
  - use the pinned endpoint and checks in [source-acceleration-phase2-batch6-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md)
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `bart-gtfs-realtime`.

Owner: Features/Webcam AI.

Goal:
- Add one bounded BART GTFS-realtime operational-context source using one public feed family only.

Scope:
- Pick one feed family only: vehicle positions, trip updates, or alerts.
- Preserve feed-family semantics and freshness.
- No broad transit analytics platform scope and no multi-feed merge in the first patch.

Observe -> Orient expectations:
- Observe: one pinned public GTFS-realtime feed family.
- Orient: normalized operational-context records with provenance, freshness, and feed-family labels.

Implementation requirements:
- Fixture-first only.
- Keep source mode, source health, fetched time, freshness, provenance, and caveats explicit.
- Export metadata must preserve source id, source URL, feed family, fetched time, freshness summary, and service-context caveats.

Do not:
- widen into full transit analytics
- merge all realtime feed families at once
- invent network-wide outage or rider-impact claims beyond source records
```

## 5. `nasa-power-meteorology-solar`

- Recommended owner agent: `geospatial`
- Current status: `assignment-ready`
- Goal:
  Add one bounded NASA POWER point-query context source so geospatial consumers can use official modeled meteorology or solar context without presenting climatology or modeled values as observed local event truth.
- First safe slice:
  One point-based meteorology or solar context query only.
- Observe input:
  One pinned public NASA POWER point query for a small bounded parameter set.
- Orient output:
  Normalized point-context record with coordinates, parameter values, time range, provenance, and explicit modeled-context caveats.
- Evidence basis:
  `modeled` or `contextual`
- Source mode/health expectation:
  Fixture-first by default, with explicit source mode and freshness fields that distinguish query execution time from modeled time range.
- Caveats:
  - modeled context only
  - one point query only
  - preserve variable/time-range semantics
  - do not present results as direct incident or observation truth
- Export metadata:
  - source id and source URL
  - coordinates
  - parameter set
  - time range
  - fetched time
  - modeled-context caveats
- Fusion-layer mapping:
  - Observe: bounded point-based modeled context query
  - Orient: normalized local context values by parameter and time range
  - Prioritize: bounded parameter/time-range filtering only
  - Explain: modeled-context summary with provenance and caveats
  - Act: context enrichment only, not local impact inference
- Runtime/interface note:
  Shared backend/core only. Safe for desktop and backend-only runtime; no remote-access implications.
- Do-not-do list:
  - do not present modeled climatology as observed local event truth
  - do not widen into bulk regional grids
  - do not infer downstream energy, weather, or infrastructure impacts from one query
- Validation commands:
  - use the pinned endpoint and checks in [source-acceleration-phase2-batch6-briefs.md](/C:/Users/mike/11Writer/app/docs/source-acceleration-phase2-batch6-briefs.md)
- Paste-ready prompt:

```text
Implement the first-slice connector for source id `nasa-power-meteorology-solar`.

Owner: Geospatial AI.

Goal:
- Add one bounded NASA POWER point-query context source for modeled meteorology or solar context.

Scope:
- One point query only.
- One small bounded parameter set only.
- No bulk grids, no regional sweeps, and no unrelated POWER product expansion.

Observe -> Orient expectations:
- Observe: one official public point query.
- Orient: normalized modeled-context values with coordinates, time range, provenance, and caveats.

Implementation requirements:
- Fixture-first only.
- Keep source mode, source health, fetched time, modeled time range, provenance, and caveats explicit.
- Export metadata must preserve source id, source URL, coordinates, parameter set, time range, fetched time, and modeled-context caveats.

Do not:
- present modeled climatology as observed local event truth
- widen into bulk-grid ingestion
- infer downstream impacts from one modeled point query
```

## Secondary Packets Not Included In The Core Five

- `anchorage-vaac-advisories`
  - same bounded aerospace advisory pattern as Washington VAAC
  - left out of the core five because one VAAC packet is enough for first routing and avoids redundant aerospace copy-paste noise
- `tokyo-vaac-advisories`
  - same bounded aerospace advisory pattern as Washington VAAC
  - left out of the core five for the same reason as Anchorage
- `nrc-event-notifications`
  - clean assignment-ready geospatial context source, but lower immediate routing value than the top five because the event family is narrower and more specialized
- `cisa-cyber-advisories`
  - assignment-ready under `connect`, but outside the strongest spatial/environmental/operational routing set for this packet wave
