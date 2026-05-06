# Meteoalarm Atom Feeds

## Route

- `GET /api/events/meteoalarm/country-warnings`

## Bounded Slice

- source id: `meteoalarm-atom-feeds`
- one official Meteoalarm Atom country feed only
- current pinned feed in this slice:
  - `https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-norway`
- fixture-first Atom parsing posture
- bounded warning-entry normalization only

## Query Parameters

- `q`
  - optional substring filter across title, summary, area label, and country
- `limit`
- `sort`
  - `newest`
  - `title`

## Normalized Fields

- `entryId`
- `title`
- `country`
- `areaLabel`
- `updatedAt`
- `publishedAt`
- `link`
- `summary`
- `sourceUrl`
- `sourceMode`
- `caveat`
- `evidenceBasis=advisory`

## Guardrails

- advisory/contextual warning-distribution records only
- one country feed only in this slice
- no multi-country sweep
- no RSS fallback
- no HTML scraping fallback
- Meteoalarm remains normalized warning context, not stronger authority than the underlying national warning provider
- no damage, impact, certainty, responsibility, legal, or action claims from Atom entry text
- free-form entry text remains inert source data only

## Fixture Coverage

- `app/server/data/meteoalarm_atom_norway_fixture.xml`
- `app/server/data/meteoalarm_atom_norway_empty_fixture.xml`

## Validation

- `app/server/tests/test_meteoalarm_atom_feed.py`
