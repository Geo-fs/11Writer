# Reference Module

## Purpose

The reference module is the platform's authoritative geospatial world model. It owns canonical facilities, navigation objects, fixes, and place references, plus the lookup and linkage logic other subsystems should call after they finish their own live-data normalization.

This module is intentionally separate from:

- webcam fetching and review ingestion
- aircraft polling and track ingestion
- satellite propagation and caching
- current or future radio stream ingestion

Those systems should remain responsible for fetching and validating their own live data. They should call the reference module only to resolve that data onto canonical real-world objects.

## Canonical IDs

Every object is exposed through a deterministic `ref_id`:

`ref:{object_type}:{dataset}:{normalized-source-key}`

Examples:

- `ref:airport:ourairports:ksea`
- `ref:runway:ourairports:ksea:16l:34r`
- `ref:navaid:ourairports:sea`
- `ref:fix:faa-fixes:summa`
- `ref:region:places:city:seattle-wa`

`object_type` is one of:

- `airport`
- `runway`
- `navaid`
- `fix`
- `region`

`ref_id` is the only stable cross-system identifier that downstream consumers should persist.

## Canonical Object Model

Shared fields on every reference object:

- `ref_id`
- `object_type`
- `canonical_name`
- `primary_code`
- `source_dataset`
- `source_key`
- `status`
- `country_code`
- `admin1_code`
- `centroid_lat`
- `centroid_lon`
- `bbox_min_lat`, `bbox_min_lon`, `bbox_max_lat`, `bbox_max_lon`
- `geometry_json`
- `coverage_tier`
- `search_text`

Normalized detail tables add object-specific fields:

- Airports:
  - `icao_code`, `iata_code`, `local_code`, `gps_code`
  - `airport_type`, `elevation_ft`
  - `municipality`, `iso_region`
  - `scheduled_service`
  - `continent_code`, `timezone_name`, `keyword_text`
- Runways:
  - `airport_ref_id`
  - `le_ident`, `he_ident`
  - `length_ft`, `width_ft`, `surface`
  - `le_heading_deg`, `he_heading_deg`
  - `le_latitude_deg`, `le_longitude_deg`, `he_latitude_deg`, `he_longitude_deg`
  - `closed`, `lighted`, `surface_category`
  - `threshold_pair_code`
  - `center_latitude_deg`, `center_longitude_deg`
- Navaids:
  - `ident`, `navaid_type`, `frequency_khz`, `elevation_ft`
  - `associated_airport_ref_id`
  - `power`, `usage`, `magnetic_variation_deg`, `name_normalized`
- Fixes:
  - `ident`, `fix_type`, `jurisdiction`, `usage_class`
  - `artcc`, `state_code`, `route_usage`
- Regions:
  - `region_kind`, `parent_ref_id`, `geometry_quality`
  - `place_class`, `population`, `rank`

Aliases live in `reference_aliases`. They are intentionally separate from base tables so new alias classes can be added without widening every object schema.

## Alias And Code Precedence

Airport code priority is locked to:

`ICAO > IATA > FAA/local > GPS`

Alias classification currently uses:

- `icao`
- `iata`
- `faa`
- `gps`
- `local`
- `name`
- `phonetic`
- `alternate`

Use `primary_code` only as a convenience display/search field. If the distinction matters, read the object-specific code fields instead of assuming `primary_code` means the same thing across all object types.

## Source And Trust Model

Current ingestion inputs:

- `ourairports`
  - baseline global airports, runways, navaids
- `places`
  - curated regional and place hierarchy
- `faa-fixes`
  - stronger U.S. fix coverage
- `airport-codes`
  - additive airport code and alias enrichment

The module uses manifest-driven ingestion with explicit:

- source name
- parser id
- source mode: `local` or `remote`
- expected files
- version
- checksum
- precedence

Normalization rules:

- `ref_id` format is deterministic and stable.
- Enrichment datasets merge into existing canonical objects when codes or normalized identity strongly match.
- Higher-trust sources may overwrite weaker fields; otherwise enrichers fill missing data.
- Missing records are marked inactive rather than hard-deleted.
- Re-ingestion is expected to be idempotent.

`coverage_tier` values:

- `authoritative`
- `curated`
- `baseline`

Downstream consumers should not assume global completeness is uniform across all object types. Fix coverage is intentionally stronger where authoritative FAA input exists.

## Search Contract

Primary endpoint:

- `GET /api/reference/search`

Supported inputs:

- `q`
- `types[]`
- `country`
- `admin1`
- `limit`

Ranking is precision-first and deterministic:

1. exact ICAO
2. exact IATA
3. exact FAA/local/GPS code
4. exact runway threshold pair
5. exact navaid ident
6. exact fix ident
7. exact canonical name
8. exact alias
9. prefix matches
10. conservative fuzzy fallback on a small candidate set

Search response metadata:

- `summary`
- `rank_reason`
- `matched_field`
- `matched_value`
- `score`

Important fields in `summary`:

- `object_display_label`
- `code_context`
- `aliases`

Recommended consumer behavior:

- treat `rank_reason` as the stable explanation for why a result surfaced
- prefer the first result for machine linkage only when the caller already has strong context
- show `object_display_label` in analyst-facing lists instead of reconstructing display strings client-side

## Spatial And Geometry Semantics

Spatial helpers are object-aware:

- airport distance: centroid
- runway distance: threshold segment
- navaid/fix/place distance: centroid
- region distance: centroid, with containment checked separately

Reusable geometry helpers include:

- great-circle distance
- initial bearing
- heading normalization
- reciprocal runway heading
- runway threshold extraction
- runway centerpoint
- runway bearing from thresholds
- point-to-segment runway distance
- object-relative distance and bearing dispatch
- airport influence radius heuristics
- bbox intersection
- point-in-polygon

Consumers should not implement their own runway proximity math unless they need a domain-specific override. The reference module is the contract for shared spatial semantics.

## Nearest And Nearby Endpoints

Generic endpoints:

- `GET /api/reference/nearby`
- `GET /api/reference/in-bounds`
- `GET /api/reference/relationships`

Specialized endpoints:

- `GET /api/reference/nearest/airport`
- `GET /api/reference/nearest/runway-threshold`
- `GET /api/reference/nearest/navaid`
- `GET /api/reference/nearby/fixes`
- `GET /api/reference/nearby/regions`

Nearby responses now include:

- `summary`
- `distance_m`
- `bearing_deg`
- `geometry_method`

`geometry_method` values:

- `centroid`
- `segment`
- `containment`

Use the specialized endpoints when the caller already knows the semantic target. They provide cleaner ranking and more predictable downstream behavior than a broad mixed-type `/nearby` call.

## Relationship Semantics

`GET /api/reference/relationships` returns:

- `from_ref_id`
- `to_ref_id`
- `from_object_type`
- `to_object_type`
- `distance_m`
- `initial_bearing_deg`
- `contains`
- `intersects`
- `same_airport`
- `same_region_lineage`
- `contains_point_semantics`

`contains` is currently most meaningful when the left-hand object is a region and the right-hand object has a centroid.

## Linkage Contract For Live Systems

The reference module provides two distinct linkage layers:

- read-only candidate suggestion
- explicit reviewed-link persistence

Suggestion endpoints never mutate `reference_links`. Reviewed links are written only through the explicit reviewed-link API.

Generic endpoint:

- `GET /api/reference/resolve-link`

Preferred specialized endpoints:

- `GET /api/reference/link/webcam`
- `GET /api/reference/link/aircraft`
- `GET /api/reference/link/radio`

Supported response shape:

- `primary`
- `alternatives`
- `context`
- `persisted_links`
- `results`

Each candidate includes:

- `summary`
- `confidence`
- `method`
- `reason`
- `score`
- `confidence_breakdown`

`persisted_links` contains durable reviewed attachments for the same external object when the caller supplies:

- `external_system`
- `external_object_id`

Context includes:

- `containing_regions`
- `nearest_airport`
- `nearest_place`

### Webcam linkage

Preferred resolution order:

1. explicit facility code or exact name
2. nearest runway threshold within a strict radius, optionally heading-aware
3. nearest airport
4. containing or nearby place context

Recommended usage:

- pass `heading_deg` when the camera orientation is known or estimated
- prefer `/link/webcam` over the generic resolver
- treat `results` as suggestions only until a reviewed link is created

### Aircraft linkage

Preferred resolution order:

1. nearest airport
2. nearest runway only when proximity strongly suggests airport-surface context
3. containing or nearby region context
4. optional nearby navaid/fix context as secondary analyst context

Recommended usage:

- use `/link/aircraft` for arrival/departure context, ground proximity, and regional attribution
- do not assume runway linkage is appropriate for every airborne point

### Radio linkage

Preferred resolution order:

1. explicit facility or ident match
2. nearby navaid with frequency support
3. airport context
4. place or region context

Recommended usage:

- pass `frequency_khz` when available
- prefer `/link/radio` over generic search when the source is radio/facility oriented

## Reviewed Link Contract

Durable reviewed links are stored in `reference_links` and are intended for analyst-approved overrides or confirmations.

Minimal creation endpoint:

- `POST /api/reference/reviewed-links`

Readback endpoint:

- `GET /api/reference/reviewed-links`

Resolved best-current-attachment endpoint:

- `GET /api/reference/resolved-attachment`

Required create fields:

- `external_system`
- `external_object_type`
- `external_object_id`
- `ref_id`
- `link_kind`
- `confidence`
- `method`
- `reviewed_by`

Optional review metadata:

- `review_status`
- `review_source`
- `notes`
- `candidate_method`
- `candidate_score`
- `override_existing`

`review_status` values:

- `approved`
- `rejected`
- `superseded`

Semantics:

- `approved`
  - active analyst-reviewed link
- `rejected`
  - reviewed and intentionally not accepted
- `superseded`
  - previously approved link that was replaced by a newer reviewed override

Current override behavior is intentionally narrow:

- when a new `primary` reviewed link is created with `override_existing=true` and `review_status=approved`
- existing approved `primary` links for the same external object are marked `superseded`
- suggestion endpoints remain read-only and continue returning fresh candidates independently

Automated candidates differ from reviewed links:

- candidates are ephemeral and recalculated
- candidates carry ranking metadata such as `score`, `method`, and `confidence_breakdown`
- reviewed links are durable records with reviewer identity, review timestamp, and review status

Recommended consumer behavior:

1. call a link suggestion endpoint
2. present `primary`, `alternatives`, and `context` to an analyst or review workflow
3. persist the approved attachment through `POST /api/reference/reviewed-links`
4. later fetch `GET /api/reference/reviewed-links` or use `persisted_links` on suggestion responses for the durable answer

## Resolved Best Attachment

`GET /api/reference/resolved-attachment` answers a narrow consumer question:

`What is the best current reference attachment for this external object?`

Inputs:

- `external_system`
- `external_object_type`
- `external_object_id`
- optional live resolution context such as `lat`, `lon`, `q`, `facility_code`, `frequency_khz`, `heading_deg`

Resolution order:

1. approved persisted reviewed link
2. otherwise best fresh suggestion
3. otherwise no match

Response fields:

- `resolution_source`
  - `persisted-reviewed`
  - `fresh-suggestion`
  - `none`
- `resolved_reviewed_link`
- `resolved_suggestion`
- `alternatives`
- `persisted_links`
- `context`

### Resolution Source Handling

When `resolution_source = persisted-reviewed`:

- treat `resolved_reviewed_link` as the authoritative current attachment
- use `resolved_suggestion` only as absent
- keep `alternatives` available for analyst review or drift detection, not as the active attachment
- if fresh suggestions disagree with the reviewed attachment, do not silently replace the reviewed attachment

When `resolution_source = fresh-suggestion`:

- treat `resolved_suggestion` as the best available machine answer
- do not persist it automatically unless your workflow explicitly approves machine-only persistence
- show `alternatives` in review UIs when confidence is marginal or the object is operationally important

When `resolution_source = none`:

- treat the object as unresolved
- do not invent or cache a synthetic attachment
- optionally surface `context` if present, but keep the object unlinked until a later suggestion or review event

Semantics:

- `resolved_reviewed_link`
  - the durable current answer when an approved reviewed link exists
- `resolved_suggestion`
  - the best live machine suggestion when no approved reviewed link exists
- `alternatives`
  - fresh machine alternatives only
- `persisted_links`
  - durable reviewed history visible to consumers, including superseded records when explicitly requested elsewhere

### Runtime Fields Vs Audit Fields

Safe for normal runtime display:

- `resolved_reviewed_link.summary.object_display_label`
- `resolved_reviewed_link.summary.code_context`
- `resolved_suggestion.summary.object_display_label`
- `resolved_suggestion.summary.code_context`
- `context.nearest_airport`
- `context.nearest_place`
- `context.containing_regions`

Safe for runtime logic:

- `resolution_source`
- `resolved_reviewed_link.summary.ref_id`
- `resolved_suggestion.summary.ref_id`
- `resolved_reviewed_link.link_kind`
- `resolved_reviewed_link.review_status`

Audit or review oriented fields:

- `alternatives`
- `persisted_links`
- `resolved_reviewed_link.reviewed_by`
- `resolved_reviewed_link.reviewed_at`
- `resolved_reviewed_link.review_source`
- `resolved_reviewed_link.candidate_method`
- `resolved_reviewed_link.candidate_score`
- `resolved_suggestion.score`
- `resolved_suggestion.confidence_breakdown`

Expected disagreement behavior:

- if an approved reviewed link and fresh suggestion disagree, the approved reviewed link remains the active answer
- the fresh suggestion remains visible only as review context
- consumers should route disagreements to analyst or QA workflows instead of auto-flipping the live attachment

Recommended usage:

- call `resolved-attachment` for normal downstream consumption when a system needs one current answer
- call raw link suggestion endpoints when an analyst or review UI needs candidate inspection
- call reviewed-link endpoints when creating or auditing durable overrides

### Integration Examples

#### Webcam consumer

Typical read path:

```http
GET /api/reference/resolved-attachment?external_system=webcams&external_object_type=webcam&external_object_id=cam-123&lat=47.4489&lon=-122.3094&heading_deg=180
```

Typical consumer behavior:

1. if `resolutionSource` is `persisted-reviewed`, render `resolvedReviewedLink.summary.objectDisplayLabel`
2. if `resolutionSource` is `fresh-suggestion`, render `resolvedSuggestion.summary.objectDisplayLabel` with an unreviewed badge if your UI supports it
3. if `resolutionSource` is `none`, leave the camera unattached

Example response shape:

```json
{
  "externalSystem": "webcams",
  "externalObjectType": "webcam",
  "externalObjectId": "cam-123",
  "resolutionSource": "persisted-reviewed",
  "resolvedReviewedLink": {
    "reviewStatus": "approved",
    "summary": {
      "refId": "ref:airport:ourairports:ksea",
      "objectDisplayLabel": "KSEA Seattle-Tacoma International Airport"
    }
  },
  "alternatives": [
    {
      "method": "spatial-proximity",
      "summary": {
        "refId": "ref:runway:ourairports:ksea:16l:34r",
        "objectDisplayLabel": "Runway 16L/34R"
      }
    }
  ]
}
```

#### Radio consumer

Typical read path:

```http
GET /api/reference/resolved-attachment?external_system=radio&external_object_type=radio&external_object_id=feed-789&lat=34.8537&lon=-116.7867&frequency_khz=113.2
```

Typical consumer behavior:

1. use `resolvedReviewedLink` when present
2. otherwise use `resolvedSuggestion`
3. keep `alternatives` and `persistedLinks` out of the main runtime display unless the UI is a review tool

#### Generic external-object consumer

If the external system is not webcam- or radio-specific, call:

```http
GET /api/reference/resolved-attachment?external_system=osint-panel&external_object_type=external-object&external_object_id=obj-42&q=KSEA
```

This lets a generic consumer still benefit from the same precedence rules without re-implementing reviewed-link lookup plus live suggestions.

## Recommended Consumer Patterns

For webcams:

1. normalize the live camera payload in the webcam subsystem
2. call `/api/reference/link/webcam` for analyst review flows
3. if an analyst approves or overrides the match, call `POST /api/reference/reviewed-links`
4. for normal downstream use, call `/api/reference/resolved-attachment`

For aircraft:

1. normalize the live aircraft point or track event
2. call `/api/reference/link/aircraft`
3. use the primary result for context only when the event is near ground infrastructure

For radio feeds:

1. normalize the radio source metadata
2. call `/api/reference/link/radio` for analyst review flows
3. use `context` to enrich UI labels even when the top candidate is ambiguous
4. persist an approved facility attachment through the reviewed-link API when a human confirms the mapping
5. use `/api/reference/resolved-attachment` when a consumer needs the best current facility attachment without re-implementing precedence logic

For search UIs:

1. use `/api/reference/search`
2. display `object_display_label`
3. show `rank_reason` or humanized result context only when needed for debugging or analyst review

## Ingestion Usage

Baseline local-file usage:

```bash
cd app/server
python -m src.reference.ingest.cli ourairports path/to/ourairports --database-url sqlite:///./data/reference.db --version 2026-04
python -m src.reference.ingest.cli places path/to/places --database-url sqlite:///./data/reference.db --version 2026-04
python -m src.reference.ingest.cli fixes path/to/faa-fixes --database-url sqlite:///./data/reference.db --version 2026-04
python -m src.reference.ingest.cli airport-codes path/to/airport-codes --database-url sqlite:///./data/reference.db --version 2026-04
```

Hybrid staging is supported through manifest metadata. Remote fetch helpers are intentionally limited to small, stable, documented sources and remain separate from parser logic.

## Non-Goals

The reference module does not:

- fetch webcam data
- ingest or stream radio audio
- own aircraft polling
- own satellite polling
- replace subsystem-specific validation rules
- guarantee that every linkage candidate should be auto-persisted without analyst review

## Persistence Boundary

`reference_links` is now the durable store for explicit reviewed attachments. It is still not mutated by generic suggestion endpoints. Write behavior is intentionally narrow and explicit through the reviewed-link API so auditability stays clear.

## Guidance For Other Agents

- Use this module as the canonical resolver for facility, runway, navaid, fix, and place identity.
- Do not duplicate reference ranking or geometry logic in other services.
- Do not modify live ingestion pipelines just to make them reference-aware.
- Attach live objects after their own normalization, using `ref_id` as the durable bridge.
- If you need a new source-specific enricher, add it under `src/reference/ingest` with manifest metadata and idempotent merge behavior.
- For day-to-day read paths, prefer `resolved-attachment` over manually combining suggestions and reviewed-link history.
