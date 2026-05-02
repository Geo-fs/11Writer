# Netherlands RWS Waterinfo Endpoint Verification

This memo narrows the current `netherlands-rws-waterinfo` candidate to one bounded official Rijkswaterstaat WaterWebservices slice.

Purpose:

- decide whether the source should remain held, move to assignment-ready, or be rejected
- pin the exact official machine endpoints for the first safe slice
- prevent Marine from inheriting a vague viewer/app-routing task

## Classification Result

- Classification: `assignment-ready`
- Scope qualifier:
  - only for one narrow POST-based water-level context slice
  - not for the broader Waterinfo portal, viewer flows, or mixed service families

## Verified Official Sources

- Open data landing:
  - [Rijkswaterstaat open data](https://www.rijkswaterstaat.nl/zakelijk/open-data)
- Waterdata landing:
  - [Rijkswaterstaat waterdata](https://rijkswaterstaatdata.nl/waterdata/)
- Official WaterWebservices documentation:
  - [WaterWebservices beta docs](https://rijkswaterstaatdata.nl/waterdata/WaterWebservices.php)

## Verified Machine Endpoints

Use the newer `ddapi20-waterwebservices` family for the first slice.

- Metadata catalog:
  - `POST https://waterwebservices.apps.rijkswaterstaat.nl/ddapi20-waterwebservices/api/METADATASERVICES_DBO/OphalenCatalogus`
- Latest observations:
  - `POST https://waterwebservices.apps.rijkswaterstaat.nl/ddapi20-waterwebservices/api/ONLINEWAARNEMINGENSERVICES_DBO/OphalenLaatsteWaarnemingen`

These are official machine endpoints and are sufficient for one bounded metadata-plus-latest-water-level slice.

## Auth / Signup Posture

- Current posture:
  - official public webservice documentation exists
  - no login, signup, email request, or CAPTCHA is documented for the pinned first-slice endpoints
- Caveat:
  - the official docs mention header handling and future API-key posture may change
  - that is not a blocker for the current no-signup classification, but it must remain documented as a live-mode caveat

## First Safe Slice

- one bounded station or water-level context slice only
- recommended shape:
  - use `OphalenCatalogus` to pin one bounded station/parameter set
  - use `OphalenLaatsteWaarnemingen` for latest readings only
- intended semantics:
  - hydrology/context only
  - no flood-impact, inundation, navigation-safety, or operational-failure claims

## Why This Is No Longer Held

- the earlier blocker was exact endpoint pinning separate from viewer/app routing
- the official WaterWebservices documentation now provides concrete machine endpoints for the first safe slice
- that is enough to move this source from vague portal-level `needs-verification` into narrow-slice `assignment-ready`

## Remaining Caveats

- POST-body contract discipline is required
- the first slice must stay bounded to one metadata-plus-latest-reading flow
- viewer pages, dashboards, and app-routed flows are not the contract
- broad Waterinfo family ingestion is still out of scope
- any future auth/API-key change should downgrade the source immediately until re-verified

## Do Not Do

- do not build against the viewer pages
- do not treat the whole Waterinfo portal as one connector
- do not widen into historical, forecast, or multi-family service ingestion in the first patch
- do not infer inundation, flood impact, safety, causation, or action guidance from water-level values alone

## Recommended Status Interpretation

- Source-status truth:
  - `assignment-ready`
- Routing truth:
  - not the immediate next Marine assignment while `france-vigicrues-hydrometry` is still the active lane
  - acceptable as the next bounded Marine source after the active hydrology lane stabilizes

## Recommended Next Step

- update the May 2026 packet set and source-status docs so `netherlands-rws-waterinfo` is:
  - no longer treated as a vague portal-level hold
  - still constrained to one narrow POST-based WaterWebservices slice

## Current Repo Status Note

- Marine now has a backend-first, fixture-first implementation for this bounded slice at:
  - `GET /api/marine/context/netherlands-rws-waterinfo`
- That implementation remains intentionally narrow:
  - metadata catalog plus latest water-level observations only
  - no portal/viewer ingestion
  - no historical or forecast expansion
