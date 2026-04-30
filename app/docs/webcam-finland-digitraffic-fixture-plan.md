# Finland Digitraffic Fixture Plan

This document prepares the first deterministic fixture slice for [`finland-digitraffic-road-cameras`](/C:/Users/mike/11Writer/app/server/src/services/camera_registry.py).

Current source lifecycle status:

- source id: `finland-digitraffic-road-cameras`
- onboarding state: `candidate`
- endpoint verification status: `machine-readable-confirmed`
- recommended next state from the graduation planner: `approved-unvalidated-candidate`
- ingest status: disabled
- connector status: fixture-first connector implemented, but still sandbox-only and not validated
- source-ops visibility: sandbox connector metadata is exposed so operators can see the latest fixture-backed validation-style import result without treating the source as active ingest

This is a planning document only. It does not activate the source.

## First slice

The first webcam-owned slice is:

- Digitraffic road weather camera stations

Out of scope for this slice:

- rail Digitraffic APIs
- marine Digitraffic APIs
- broader Finland transport integration

## Expected source shape

The current documented station endpoint is:

- `https://tie.digitraffic.fi/api/weathercam/v1/stations`

Current connector mode defaults:

- `FINLAND_DIGITRAFFIC_WEATHERCAM_MODE=fixture`
- `FINLAND_DIGITRAFFIC_WEATHERCAM_FIXTURE_PATH=./app/server/data/finland_digitraffic_weathercam_fixture.json`
- live endpoint support is optional and not the default

Sandbox visibility fields:

- `sandboxImportAvailable=true`
- `sandboxImportMode=fixture`
- `sandboxConnectorId=FinlandDigitrafficWeatherCamConnector`
- `lastSandboxImportAt`
- `lastSandboxImportOutcome`
- `sandboxDiscoveredCount`
- `sandboxUsableCount`
- `sandboxReviewQueueCount`
- `sandboxValidationCaveat`

Interpretation:

- these fields summarize the fixture-backed validation-style import path only
- they do not mark the source validated
- they do not enable scheduled refresh
- they are intended to help operators judge mapping progress and review burden

Observed and documented fields to design around:

- top-level `features[]`
- feature `id`
- feature `geometry.type`
- feature `geometry.coordinates`
- feature `properties.id`
- feature `properties.name`
- feature `properties.collectionStatus`
- feature `properties.dataUpdatedTime`
- feature `properties.presets[]`
- preset `id`
- preset `inCollection`
- station `state`

The current docs also state:

- preset image URLs follow `https://weathercam.digitraffic.fi/{presetId}.jpg`
- thumbnail form follows `https://weathercam.digitraffic.fi/{presetId}.jpg?thumbnail=true`
- camera images update about every 10 minutes

## Mapping plan

Station and camera identity:

- source id stays `finland-digitraffic-road-cameras`
- station identifier should come from feature `id` or `properties.id`
- child camera/preset identifier should come from `properties.presets[].id`
- final internal camera record ids should be station-plus-preset scoped, not station-only

Coordinates:

- use `geometry.coordinates[0]` as longitude
- use `geometry.coordinates[1]` as latitude
- classify as exact only when the coordinates array is present and numeric

Orientation:

- no orientation field is currently verified from the station endpoint
- default orientation should be `unknown`
- do not infer heading from road name or station name

Direct image URL assumptions to verify:

- initial connector plan may construct image URLs from preset ids using the documented `weathercam.digitraffic.fi/{presetId}.jpg` pattern
- do not treat this as final until fixture-backed normalization and source-health checks confirm the behavior
- if a preset is not in collection, it should not be treated as an active direct-image camera
- current sandbox connector maps in-collection presets to direct-image URLs and leaves out-of-collection presets as unavailable, review-needed cameras

Station versus preset handling:

- a station may contain multiple presets
- each preset should become its own camera-like view record if `inCollection=true`
- station-level metadata should be copied to each preset-derived camera record
- presets with `inCollection=false` should either be skipped or emitted as review-needed depending on connector policy chosen later

Unavailable images:

- if the preset id exists but a direct image fetch later fails, represent that as frame unavailable or blocked rather than dropping the camera silently
- if docs and station metadata disagree, create a review item rather than claiming direct-image confidence

Review states:

- missing coordinates -> review-needed
- orientation unknown -> allowed but explicit
- preset not in collection -> review-needed or skipped, depending on later connector decision
- direct-image pattern mismatch -> review-needed
- current sandbox connector keeps preset-not-in-collection records as degraded review items instead of silently skipping them

Source-health fields needed later:

- last metadata refresh time
- last frame probe time
- last HTTP status
- rate-limit or backoff observation
- stale detection window based on the documented image update cadence

## Fixture set to create later

Minimum fixture set:

1. successful stations response
   - one station
   - multiple presets
   - at least one `inCollection=true`
   - exact coordinates
2. partial station response
   - one preset not in collection
   - one station with missing optional `state`
3. degraded response
   - empty `features`
   - or one station with malformed preset array
4. optional data endpoint sample
   - if later connector work needs `/api/weathercam/v1/stations/data`

## Synthetic fixture skeleton

The repo now includes a tiny synthetic fixture skeleton at:

- [`app/server/data/finland_digitraffic_weathercam_fixture.json`](/C:/Users/mike/11Writer/app/server/data/finland_digitraffic_weathercam_fixture.json)

This file is intentionally small and synthetic:

- not a full live payload
- not a bulk export
- enough only to lock the expected station/preset shape for later connector work

## Graduation gates before activation

Before this source can move beyond candidate-only:

- create representative success and degraded fixtures
- confirm station-to-preset normalization rules
- confirm direct image URL behavior and health semantics
- define review handling for out-of-collection presets
- add connector normalization tests
- add source-health tests
- complete compliance and attribution review

## Do not do

- do not enable ingestion from this document
- do not scrape interactive pages
- do not broaden ownership into rail or marine Digitraffic in this slice
- do not claim validated status from endpoint verification alone
