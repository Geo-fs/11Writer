# OSINT Framework Intake Routing Memo

This memo converts Wonder's OSINT Framework audit into candidate-only planning input for 11Writer.

Use it to answer:

- what the OSINT Framework audit is allowed to inform
- which audit entries can enter bounded candidate review
- which entries should stay held, rejected, or manual-review only
- which lane should own next review if a candidate survives intake

Status rule:

- OSINT Framework listings are discovery input only
- Wonder audit artifacts are research input only
- neither proves no-auth safety, legality, authority, truth, attribution, causation, actionability, or implementation readiness
- normal status promotion still belongs to [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md:1), [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md:1), and [source-workflow-validation-plan.md](/C:/Users/mike/11Writer/app/docs/source-workflow-validation-plan.md:1)

Source artifacts reviewed:

- [osint_framework_best_fit_audit.md](/C:/Users/mike/11Writer/output/osint_framework_best_fit_audit.md:1)
- [osint_framework_best_fit_audit.csv](/C:/Users/mike/11Writer/output/osint_framework_best_fit_audit.csv:1)
- [osint_framework_best_fit_audit.json](/C:/Users/mike/11Writer/output/osint_framework_best_fit_audit.json:1)

## Audit Summary

- total entries checked: `152`
- reachable: `124`
- unreachable: `28`
- machine-readable mix:
  - `yes`: `5`
  - `api-claimed-needs-endpoint`: `46`
  - `no`: `101`
- Wonder suitability buckets:
  - `review-directory-candidate`: `63`
  - `candidate-source-packet`: `30`
  - `hold-unreachable-or-blocked-check-needed`: `28`
  - `candidate-connector-after-endpoint-review`: `19`
  - `manual-review-only`: `12`

Interpretation rule:

- the audit is useful as candidate triage input
- it is not a clean assignment-ready source pack
- most entries still need endpoint pinning, policy review, or machine-readability confirmation before they should leave candidate state

## Compatible Intake Classes

These classes can enter bounded candidate review if they also satisfy the normal no-auth and machine-readable rules:

- official advisories or public status feeds with pinned machine endpoints
- transport or infrastructure context feeds with stable public machine output
- environmental or hazard authority feeds with stable public machine output
- static or reference datasets with direct public download or API access
- bounded RSS, Atom, XML, JSON, GeoJSON, CSV, or KML sources with explicit public access

These classes should usually stay candidate-only until a narrower endpoint is pinned:

- review directories
- tool indexes
- HTML search tools
- source catalogs
- map sites
- article collections
- mixed-format repositories

## Excluded Or High-Risk Classes

Default hold or reject classes from this audit:

- browser-only investigative tools
- search sites with no stable machine endpoint
- HTML-only map or lookup pages
- social, article, or link directories with no direct machine interface
- entries that imply scraping interactive web apps
- entries with hidden auth, signup, CAPTCHA, token, or controlled-access posture
- entries where the audit only proves reachability, not reusable machine-readable source value

## Candidate Intake Buckets

### `candidate-source-packet`

Use when:

- Wonder found a plausible source candidate
- a stable provider identity is clear
- a likely machine-readable endpoint family exists
- no-auth posture is plausible but still needs direct endpoint review

Next routing:

- `gather` for classification truth
- domain owner or `data` for endpoint pinning

### `candidate-connector-after-endpoint-review`

Use when:

- Wonder found a candidate that might fit 11Writer well
- endpoint structure still needs direct repo-local review
- machine-readability is plausible but not pinned tightly enough yet

Next routing:

- `gather` or `data` for endpoint review packet
- domain owner only after one bounded endpoint is pinned

### `review-directory-candidate`

Use when:

- the entry is better as a discovery aid than as a first connector
- it points to many downstream sources rather than being a clean source itself

Next routing:

- keep with `gather`
- optionally route to `data` or a domain owner only if one downstream endpoint is clearly worth isolating

### `manual-review-only`

Use when:

- the entry is HTML-heavy, investigative, map-heavy, or otherwise not machine-usable first
- it may still inspire later human review, but not immediate connector work

Next routing:

- hold with `gather`
- do not route for connector implementation

### `hold-unreachable-or-blocked-check-needed`

Use when:

- the site failed reachability checks
- endpoint posture is unclear
- auth or policy posture is too ambiguous

Next routing:

- hold or reject until direct verification changes materially

## Owner Routing

- `gather`
  - intake truth, candidate buckets, hold/reject decisions, and routing packets
- `connect`
  - shared runtime-boundary review only if a candidate overlaps source-discovery or shared tooling surfaces
- `data`
  - public advisory, feed, internet-information, news, OSINT, or mixed public-information candidates
- `geospatial`
  - environmental, hazard, weather, map-reference, hydrology, and seismic candidates
- `marine`
  - marine, coastal, port, river, and waterway candidates
- `aerospace`
  - aviation, airport, airspace, satellite, and space-context candidates
- `features-webcam`
  - camera, transport endpoint, source-ops, and endpoint-lifecycle candidates

## Required Review Gates

Every OSINT Framework candidate must preserve:

- exact source/provider identity
- exact endpoint or endpoint-pattern evidence if any
- no-auth posture
- machine-readability result
- provenance path from Wonder audit to repo review
- caveats and policy blockers
- owner recommendation
- duplicate or overlap check against existing 11Writer source docs and implemented sources

Every OSINT Framework candidate must fail closed if it encounters:

- signup
- login
- request forms
- CAPTCHA
- scraping requirements
- unstable or rotating endpoints with no pinned machine interface
- source classes that collapse into article browsing rather than reusable machine-readable ingestion

## Intake Transitions

Allowed transition pattern:

1. Wonder audit artifact
2. Gather candidate bucket
3. endpoint-review memo or bounded domain review
4. normal source brief or quick-assign packet only if the endpoint is pinned cleanly
5. normal source lifecycle after that

Disallowed shortcut:

1. Wonder audit artifact
2. direct assignment-ready status
3. direct implementation status

## Likely Safe Near-Term Uses

- feed-family inspiration for `data`
- official hazard or advisory endpoint leads for `geospatial`
- transport endpoint leads for `features-webcam`
- public reference or catalog leads for later static/reference slicing

## Do-Not-Do Summary

- do not treat the audit as approval proof
- do not treat reachability as machine-readability
- do not treat popularity as authority
- do not treat directories as final source truth
- do not route HTML-only tools as connector work
- do not infer legality or safety from presence in the OSINT Framework
- do not skip the normal no-auth, no-signup, no-CAPTCHA, no-scraping, and fixture-first rules
