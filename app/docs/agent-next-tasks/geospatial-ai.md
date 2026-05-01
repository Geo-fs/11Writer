# Geospatial AI Next Task

You are Geospatial AI, working on environmental/geospatial source features for 11Writer.

Assignment version: 2026-05-01 15:44 America/Chicago

Recent Manager/Workflow Updates:
- Environmental overview, export package, and source-health issue queue now exist as backend fusion contracts.
- Chokepoint and source-discovery work may consume geospatial context, but Geospatial must not infer damage, impact, threat, or target status.
- Keep advisory, forecast, modeled, observed, and reference evidence distinct.

Current state:
- You completed the environmental source-health issue queue/export package.
- The next useful step is a downstream report/snapshot builder that composes existing environmental export surfaces.

Mission:
- Add a backend environmental situation snapshot/report package that composes source-family overview, context export package, and source-health issue queue.

Inspect first:
- `app/server/src/services/environmental_source_families_overview_service.py`
- `app/server/src/routes/environmental_context.py`
- `app/server/tests/test_environmental_source_families_overview.py`
- `app/docs/environmental-source-family-overview.md`
- `app/docs/chokepoint-intelligence-governance-packet.md`
- `app/docs/fusion-layer-architecture.md`

Tasks:
1. Add a compact backend helper/route for an environmental situation snapshot/report package.
2. Compose the existing overview, context export package, and source-health issue queue rather than creating another source loader.
3. Include selected family filters, included/missing families, source counts, health/mode/evidence summary, caveats, review lines, issue counts, export lines, and snapshot metadata.
4. Add an optional consumer profile such as `default`, `chokepoint-context`, or `source-health-review`, with profile-specific caveat/export lines only.
5. Add tests for filtered output, missing family IDs, profile behavior, caveat preservation, issue-queue inclusion, export metadata, and no global scoring.
6. Update docs with examples and intended future report/snapshot consumer role.
7. Append your final output to `app/docs/agent-progress/geospatial-ai.md`.

Constraints:
- Backend/docs/tests only unless a typed contract update is necessary.
- No broad frontend, LayerPanel, AppShell, InspectorPanel, globe-layer, or final UI work.
- No hazard/severity/damage/impact/health-risk/threat/target scoring.
- Do not stage, commit, or push.

Validation:
- `python -m pytest app/server/tests/test_environmental_source_families_overview.py -q`
- `python -m compileall app/server/src`
- Run focused tests for any source family touched.

Final report requirements:
- Start with `Assignment version read: 2026-05-01 15:44 America/Chicago`.
- Describe snapshot/report package contract and filters.
- State caveat/evidence/source-health behavior.
- Report validation commands and results.
