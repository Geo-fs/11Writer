# Phase 2 Batch 6 Source Briefs

This pack converts Atlas AI's Batch 6 candidate backlog into Gather-owned Phase 2 source-governance truth.

Rules applied in this pass:

- no API key
- no login
- no signup
- no email/request-form gate
- no CAPTCHA
- no scraping interactive web apps
- machine-readable endpoint preferred
- fixture-first
- source health and caveats required
- no impact, damage, intent, or causation claims unless explicitly source-supported
- Atlas backlog or registry mentions do not count as implementation or validation proof

Classification meanings:

- `assignment-ready`
  - no-auth posture is clear enough for a narrow first slice now
- `needs-verification`
  - source is plausible, but endpoint pinning, auth posture, or contract shape still needs tighter confirmation
- `deferred`
  - public/open posture looks real, but the first safe slice is too broad, too binary-heavy, or too infrastructure-heavy for immediate Phase 2 assignment
- `rejected`
  - source depends on SWIM, signup, restricted portals, request-access behavior, or other patterns outside current rules

## Classification Summary

### Assignment-ready

- `geosphere-austria-warnings`
- `nasa-power-meteorology-solar`
- `first-epss`
- `nist-nvd-cve`
- `cisa-cyber-advisories`
- `nrc-event-notifications`
- `washington-vaac-advisories`
- `anchorage-vaac-advisories`
- `tokyo-vaac-advisories`
- `taiwan-cwa-aws-opendata`
- `bart-gtfs-realtime`

### Needs-verification

- `geosphere-austria-datahub`
- `poland-imgw-public-data`
- `netherlands-rws-waterinfo`
- `iaea-ines-news-events`

### Deferred

- `ecmwf-open-forecast`
- `noaa-nomads-models`
- `noaa-hrrr-model`

### Rejected

- `chmi-swim-aviation-meteo`
- `netherlands-ndw-datex-traffic`

## Manager Routing Note

Top 5 cleanest Batch 6 assignment-ready handoffs after this governance pass:

1. `geosphere-austria-warnings`
2. `washington-vaac-advisories`
3. `taiwan-cwa-aws-opendata`
4. `bart-gtfs-realtime`
5. `nasa-power-meteorology-solar`

## Hold / Reject Summary

### Rejected

- `chmi-swim-aviation-meteo`
  - SWIM-branded meteorological services are too likely to rely on restricted aviation data-access patterns for current no-signup rules
- `netherlands-ndw-datex-traffic`
  - DATEX II traffic distribution commonly implies registration, certificate handling, or controlled portal access and is not clean enough for this rule set

### Deferred

- `ecmwf-open-forecast`
  - real-time open forecast data is valuable, but the first safe slice is GRIB-heavy and too broad for the current assignment wave
- `noaa-nomads-models`
  - public and useful, but broad NCEP model access is too infrastructure-heavy for an immediate narrow connector
- `noaa-hrrr-model`
  - strong value, but HRRR model ingestion is still too binary-heavy and product-heavy for the current clean-slice bar

### Needs-verification

- `geosphere-austria-datahub`
- `poland-imgw-public-data`
- `netherlands-rws-waterinfo`
- `iaea-ines-news-events`

## Batch 6 Classification Table

| Source id | Classification | Recommended owner | Likely consumers | First safe slice | Reason | Do-not-do warning |
| --- | --- | --- | --- | --- | --- | --- |
| `geosphere-austria-warnings` | `assignment-ready` | `geospatial` | `connect`, `marine` | current warning feed only | Official warning-context fit is strong and should map cleanly into existing alert semantics. | Do not infer impact or damage from warning color alone. |
| `geosphere-austria-datahub` | `needs-verification` | `geospatial` | `connect` | one pinned weather or hydrology dataset only | DataHub posture looks promising, but dataset-level machine endpoint pinning still needs a tighter pass. | Do not treat the whole DataHub as one connector. |
| `chmi-swim-aviation-meteo` | `rejected` | `aerospace` | `connect` | none under current rules | SWIM framing is too likely to imply restricted or request-access distribution for this policy. | Do not build against SWIM or request-access aviation routes. |
| `poland-imgw-public-data` | `needs-verification` | `geospatial` | `marine`, `connect` | one bounded weather or hydrology file family only | Public repository posture may be workable, but exact machine endpoint behavior still needs tighter confirmation. | Do not normalize the whole IMGW repository in one pass. |
| `netherlands-rws-waterinfo` | `needs-verification` | `marine` | `geospatial`, `connect` | one bounded station or water-level slice only | Useful hydrology context candidate, but exact no-auth machine path still needs pinning. | Do not depend on viewer-only or app-routed calls. |
| `netherlands-ndw-datex-traffic` | `rejected` | `features-webcam` | `connect` | none under current rules | DATEX distribution is not clean enough under no-signup/no-controlled-access rules. | Do not assume DATEX means public anonymous pull access. |
| `ecmwf-open-forecast` | `deferred` | `geospatial` | `marine`, `connect` | one bounded open forecast file family only | Valuable but too binary-heavy and broad for the current immediate assignment wave. | Do not turn ECMWF open data into a bulk forecast platform. |
| `noaa-nomads-models` | `deferred` | `geospatial` | `marine`, `connect` | one bounded model file family only | Public access exists, but product-family sprawl and GRIB complexity make it a poor immediate fit. | Do not treat NOMADS as a general model-ingestion backlog dump. |
| `noaa-hrrr-model` | `deferred` | `geospatial` | `connect` | one bounded HRRR file family only | Strong value, but HRRR still inherits model-data complexity that is heavier than current Phase 2 priorities. | Do not widen into archive or full-grid ingestion. |
| `nasa-power-meteorology-solar` | `assignment-ready` | `geospatial` | `connect`, `marine` | one point-based meteorology or solar context query only | Official point-query context source with a narrow route shape and clear baseline semantics. | Do not present modeled climatology as observed local event truth. |
| `first-epss` | `assignment-ready` | `connect` | `gather` | one CVE-score lookup slice only | Officially useful risk-priority context with a narrow API fit and clear bounded semantics. | Do not present EPSS as exploit proof or incident confirmation. |
| `nist-nvd-cve` | `assignment-ready` | `connect` | `gather` | one bounded CVE detail or recent-CVE slice only | No-key lower-rate usage is acceptable and the route shape can stay narrow. | Do not assume high-rate or bulk sync behavior without keys. |
| `cisa-cyber-advisories` | `assignment-ready` | `connect` | `gather` | one advisory feed family only | Clean advisory-context source with strong provenance and bounded semantics. | Do not turn advisories into exploit or impact confirmation. |
| `nrc-event-notifications` | `assignment-ready` | `geospatial` | `connect` | one RSS/event-notification family only | Public U.S. infrastructure event notices fit a narrow evidence-aware context route. | Do not infer radiological impact beyond source text. |
| `iaea-ines-news-events` | `needs-verification` | `geospatial` | `connect` | one public event-report family only | Public event reporting exists, but the stable machine-readable path still needs tighter pinning. | Do not rely on HTML-first browsing as the contract. |
| `washington-vaac-advisories` | `assignment-ready` | `aerospace` | `geospatial`, `connect` | one volcanic ash advisory feed family only | Public ash-advisory context fits aerospace and volcano workflows with bounded semantics. | Do not claim ash dispersion precision beyond advisory text. |
| `anchorage-vaac-advisories` | `assignment-ready` | `aerospace` | `geospatial`, `connect` | one volcanic ash advisory feed family only | Same bounded ash-advisory fit as Washington VAAC with strong aviation relevance. | Do not overstate route impact from advisory text alone. |
| `tokyo-vaac-advisories` | `assignment-ready` | `aerospace` | `geospatial`, `connect` | one volcanic ash advisory feed family only | Public ash-advisory context fits aerospace and environmental hazard enrichment if kept narrow. | Do not merge VAAC products into a fake global severity scale. |
| `taiwan-cwa-aws-opendata` | `assignment-ready` | `geospatial` | `connect`, `marine` | one public AWS-backed warning or weather file family only | AWS/public-bucket posture keeps this within rules if the first slice stays bounded to one family. | Do not drift into key-gated CWA API routes. |
| `bart-gtfs-realtime` | `assignment-ready` | `features-webcam` | `connect` | one vehicle-position, trip-update, or alert feed only | Public transit realtime feed is a clean bounded operational-context candidate. | Do not widen into a full transit analytics platform in the first patch. |

## Batch 6 Notes

- Cyber-context sources in this batch are assignment-ready only for narrow advisory or scoring slices under `connect` ownership.
- Model-data sources in this batch were held back because binary-heavy file families would produce too much ingestion and validation overhead for the current clean-slice bar.
- VAAC sources are treated as advisory/contextual aerospace-environmental inputs, not as direct ash-dispersion or flight-impact proof.
- Transit and warning sources remain the strongest operationally useful Batch 6 handoffs because their first slices can stay narrow, machine-readable, and caveat-preserving.
