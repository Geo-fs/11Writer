# Spatial Intelligence Loop

The approved 11Writer operating model is the Spatial Intelligence Loop:

`Observe -> Orient -> Prioritize -> Explain -> Act`

This is the product loop for a civilian, public-source, evidence-aware fusion platform.

11Writer should ultimately behave more like an evidence-aware world-event reporting desk than a raw globe or dashboard.

That means it should:

- monitor broad public-source activity across domains
- help users ask about specific or non-specific situations
- return thorough, source-backed, caveated reports
- preserve the difference between what sources show, what the system derives, and what remains unknown

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

## Reporting Direction

11Writer should support a broad reporting workflow over the same loop:

- monitor world events across many public/no-auth sources
- answer user questions about a place, entity, timeframe, source family, or broader situation
- generate detailed reports that keep source health, evidence basis, caveats, provenance, and freshness visible
- support both "tell me about this specific thing" and "what deserves attention right now" use cases

Cross-source synthesis is allowed and important, but it is not automatic proof of:

- intent
- wrongdoing
- targeting
- threat
- impact
- causation
- action need

Those conclusions require explicit source support or must remain framed as uncertainty, review need, or competing possibilities.
