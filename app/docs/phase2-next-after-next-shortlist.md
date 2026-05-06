# Phase 2 Next-After-Next Shortlist

Use this only after the current larger controlled wave is complete.

Current mixed wave status:

- `connect`
  - `18:49` Source Discovery/runtime consolidation checkpoint is completed and the `19:15` shared reporting-loop contract wave is still in progress
- `data`
  - current-awareness digest, review/export coherence follow-on, topic-safe report export packet, and question-briefing packet are completed
- `marine`
  - current-awareness digest and source-row workflow closure packet are completed; the `19:35` question-briefing packet is still in progress
- `aerospace`
  - selected-target operational question packet, current-awareness digest, and reporting-handoff contract are completed; the `19:15` question-briefing packet is still in progress
- `geospatial`
  - `belgium-rmi-warnings` verification closed without implementation, the bounded `geoboundaries-admin` slice is completed, `meteoalarm-atom-feeds` is implemented bounded warning context, and the `19:15` environmental question-briefing packet is completed
- `features-webcam`
  - source-ops portfolio digest, review-priority packet, and the `19:15` regional portfolio packet are completed

Current routing note:

- the helper/reporting wave is no longer the main frontier for Geospatial, Data, Marine, Aerospace, or Features/Webcam
- the `2026-05-05 19:41 America/Chicago` source-expansion wave is now materially landed across:
  - `NOAA nowCOAST`
  - `National Weather Service Alerts API`
  - `RDAP`
  - `crt.sh`
  - `GPSJam`
  - `Navtex`
  - `OpenStreetMap` / `Overpass` / `Geofabrik` lead support
- keep `NASA GIBS`, `NASA Worldview`, `CelesTrak`, `Natural Earth`, `NOAA NDBC`, and `USGS earthquakes` out of fake fresh-win routing

## Recommended Next-After-Next Order

1. `user-priority-follow-on-shortlist`
   - Owner: `data`, `geospatial`, or `gather` depending on the chosen follow-on
   - Why next:
     - the first user-priority source wave is landed, so the next honest move is one bounded follow-on from [source-user-priority-follow-on-shortlist.md](/C:/Users/mike/11Writer/app/docs/source-user-priority-follow-on-shortlist.md)
   - Keep bounded:
     - one exact family only: `GeoNames`, `HDX`, `UNOSAT on HDX`, or `ReliefWeb` verification
   - Do not do:
     - do not reopen the just-landed `nowCOAST`, `NWS Alerts`, `RDAP`, `crt.sh`, `GPSJam`, `Navtex`, or OSM lead-support work as fresh intake

2. `geoboundaries-admin-follow-through`
   - Owner: `geospatial`
   - Why next:
     - useful reporting/reference follow-on now that the bounded geoBoundaries slice is implemented and Meteoalarm is also implemented
     - the backend-first geoBoundaries slice already exists, so the next honest move is consumer/export or validation follow-through rather than raw source creation
     - static/reference semantics are easy to preserve
   - Keep bounded:
     - one existing `gbOpen` country/admin slice only
   - Do not do:
     - do not frame administrative boundaries as legal, operational, or live-incident truth

3. `data-post-wave-institutional-follow-on-or-workflow-closure`
   - Owner: `data`
   - Why next:
     - the current-awareness, review/export coherence, topic-safe export, and question-briefing lanes are completed, and the user-priority source wave is landed, so the next Data move should remain on one bounded institutional follow-on or one validation closure before another broad family expansion
   - Keep bounded:
     - one topic-scoped follow-on or one explicit workflow/export closure only
   - Do not do:
     - do not reopen `world-news-awareness`, `propublica`, or `global-voices` as fresh source creation

4. `aerospace-post-briefing-smoke-execution-closure`
   - Owner: `aerospace`
   - Why next:
     - workflow evidence is still weaker than executed smoke on the current host
   - Keep bounded:
     - rerun prepared aerospace smoke on a launch-capable Windows host only
   - Do not do:
     - do not convert prepared smoke into workflow-validation proof without executed evidence

5. `webcam-post-regional-portfolio-follow-on`
   - Owner: `features-webcam`
   - Why next:
     - the portfolio digest, review-priority packet, and regional portfolio packet are completed, so one bounded comparison/report step is the next honest follow-on
   - Keep bounded:
     - compare next-safe-review posture, source-health burden, and media posture only
   - Do not do:
     - do not activate, validate, or schedule candidate-only camera sources from comparison output

## Hold Notes

- Keep `esa-neocc-close-approaches` held for now.
- Keep `belgium-rmi-warnings` verification-gated until a clean official machine-readable warning feed is pinned.
- Keep broad Data family reopening held until the topic-scoped report packet is stable.
- Keep camera candidates below implementation proof unless a controlled lane explicitly promotes them.
- Keep peer/runtime inputs below source-validation proof:
  - Atlas media geolocation hardening
  - Wonder Statuspage discovery
  - Wonder Mastodon discovery
  - Wonder Stack Exchange and seed-packet discovery
  - Wonder archive-index scan
  - Wonder mailing-list archive adapters
  - Wonder curated directory or regional-portal scan

## Routing Rules

- do not reopen completed larger-wave work as if it were fresh assignment-ready intake
- do not promote peer, runtime, helper, prepared-smoke, or candidate-only surfaces into implementation or workflow-validation proof
- prefer one bounded missing family or one validation-closure item at a time
