# Spatial Intelligence Loop

The approved 11Writer operating model is the Spatial Intelligence Loop:

`Observe -> Orient -> Prioritize -> Explain -> Act`

This is the product loop for a civilian, public-source, evidence-aware fusion platform.

## Observe

Observe means source intake.

- ingest public, no-auth feeds and fixtures
- track source mode and source health
- preserve raw timestamps, source identifiers, and provenance

## Orient

Orient means normalization and context-building.

- normalize source-specific records
- geolocate when the source supports geography
- classify record type and evidence basis
- preserve caveats
- compare sources without collapsing their meanings

## Prioritize

Prioritize means bounded attention management.

- rank anomalies, source-health issues, and review needs
- surface relevance without inventing certainty
- keep scored outputs separate from observed records

## Explain

Explain means evidence-aware presentation.

- show source basis
- show caveats
- show freshness and health
- show why a card, alert, or queue item was surfaced
- preserve export metadata and review context

## Act

Act means user decision and downstream workflow, not automated harm.

Allowed examples:

- analyst review
- report drafting
- export
- queue triage
- source follow-up
- operational review without harm recommendation

Act in 11Writer is still bounded by [safety-boundaries.md](C:/Users/mike/11Writer/app/docs/safety-boundaries.md). The platform supports awareness, review, and explanation. It does not support targeting, harmful-action recommendation, or coercive automation.
