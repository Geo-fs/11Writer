# Integration Notes

## Approved Integration Direction

This project is limited to public or explicitly approved sources.

Allowed categories:

- Google Maps Platform Photorealistic 3D Tiles
- Public aircraft APIs whose terms allow application use
- Public satellite orbital datasets
- Public map and terrain services
- Clearly authorized public camera feeds in a future optional module

Prohibited categories:

- scraped private cameras
- bypassed authentication
- restricted feeds obtained through brittle hacks
- facial recognition, license plate recognition, or personal identification
- anything positioned as real operational targeting capability

## Current Phase 1 Integrations

### Google Photorealistic 3D Tiles

- Requires a Google Maps Platform API key
- Requires billing on the Google project
- Is optional in local development because the client can fall back to Cesium terrain

### FastAPI Public Config

The API exposes only configuration needed by the UI bootstrap:

- runtime environment name
- which tiles provider is active
- whether a public Google key is available for the client
- which future feature areas are enabled

Do not expose unrelated private credentials or future vendor secrets in these endpoints.

### OpenSky Aircraft Data

- Phase 2 uses the official OpenSky `/states/all` endpoint with bounding-box queries.
- The adapter supports an optional bearer token through `OPENSKY_ACCESS_TOKEN`.
- Bounding-box polling is used to reduce payload size and keep browser/entity counts sane.
- Anonymous access may work for light local testing, but authenticated access is the safer default for ongoing use because OpenSky documents OAuth2-based authentication and rate limitations.

## Future Adapter Rules

Every live data adapter must:

- be isolated to its own module
- produce normalized entity objects
- document terms-of-use and refresh cadence
- support graceful disablement if rate limits, legal issues, or outages appear
