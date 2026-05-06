# Aerospace AI Phase 2 To Phase 3 Handoff

## Scope completed

- Completed the bounded `GPSJam` aerospace source wave as contextual GNSS-disruption awareness only.
- Completed the bounded aerospace hazard-context consumer follow-on in [aerospaceHazardContextConsumerPacket.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceHazardContextConsumerPacket.ts).
- Kept the active checkpoint small:
  no new large aerospace panel,
  no fresh source family beyond the already-in-motion hazard-context composition,
  no route-impact, outage, threat, intent, or action-recommendation semantics.
- Completed deterministic regression coverage, smoke-fixture support, prepared smoke assertions, export metadata wiring, and doc updates for the current slice.

## Current state

- Aerospace currently has bounded source/context slices for:
  NOAA AWC,
  FAA NAS,
  NASA/JPL CNEOS,
  NOAA SWPC,
  OpenSky anonymous states,
  GPSJam,
  USGS geomagnetism,
  NOAA NCEI archive metadata,
  VAAC advisory context,
  and OurAirports reference context.
- Aerospace also has higher-order workflow helpers for:
  operational context,
  context availability,
  source readiness,
  review/gap/export packages,
  report brief / handoff / question packet,
  current-awareness digest,
  workflow evidence ledger,
  workflow-validation evidence snapshot,
  and the new hazard-context consumer packet.
- The new packet is snapshot/export composition only.
  It combines:
  `gpsjamContext`,
  geospatial `NWS Alerts`,
  and geospatial `NOAA nowCOAST` layer-catalog metadata.
- Observed versus derived versus contextual posture remains explicit:
  selected-target evidence and some aircraft state are observed/session-derived,
  OpenSky comparison and GPSJam are source-reported/contextual,
  NWS Alerts are advisory/public-alert context,
  nowCOAST is contextual map-layer metadata,
  NCEI is archival metadata,
  workflow-evidence rows are validation/accounting only.

## Files and surfaces to know

- Active bounded hazard-context helper:
  [aerospaceHazardContextConsumerPacket.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceHazardContextConsumerPacket.ts)
- Existing GPSJam helper:
  [aerospaceGpsJamContext.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceGpsJamContext.ts)
- Export/metadata wiring:
  [AppShell.tsx](/C:/Users/mike/11Writer/app/client/src/features/app-shell/AppShell.tsx)
  [aerospaceExportProfiles.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceExportProfiles.ts)
- Workflow evidence surfaces:
  [aerospaceWorkflowEvidenceLedger.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceWorkflowEvidenceLedger.ts)
  [aerospaceWorkflowValidationEvidenceSnapshot.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceWorkflowValidationEvidenceSnapshot.ts)
- Higher-order aerospace reporting surfaces most likely to matter to Reporting AI:
  [aerospaceReportBriefPackage.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceReportBriefPackage.ts)
  [aerospaceSelectedTargetOperationalQuestionPacket.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceSelectedTargetOperationalQuestionPacket.ts)
  [aerospaceCurrentAwarenessDigest.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceCurrentAwarenessDigest.ts)
  [aerospaceReportingHandoffContract.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceReportingHandoffContract.ts)
  [aerospaceQuestionBriefingPacket.ts](/C:/Users/mike/11Writer/app/client/src/features/inspector/aerospaceQuestionBriefingPacket.ts)
- Client geospatial consumption hooks already used by aerospace:
  [queries.ts](/C:/Users/mike/11Writer/app/client/src/lib/queries.ts)
  Search for:
  `useNwsAlertsRecentQuery`
  `useNoaaNowCoastLayerCatalogQuery`
  `useGpsJamContextQuery`
- Smoke-fixture and prepared smoke surfaces:
  [smoke_fixture_app.py](/C:/Users/mike/11Writer/app/server/tests/smoke_fixture_app.py)
  [playwright_smoke.mjs](/C:/Users/mike/11Writer/app/client/scripts/playwright_smoke.mjs)
- Domain docs:
  [aerospace-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/aerospace-workflow-validation.md)
  [aerospace-workflow-evidence-ledger.md](/C:/Users/mike/11Writer/app/docs/aerospace-workflow-evidence-ledger.md)
  [aircraft-satellite-smoke.md](/C:/Users/mike/11Writer/app/docs/aircraft-satellite-smoke.md)
  [aerospace-source-contract-matrix.md](/C:/Users/mike/11Writer/app/docs/aerospace-source-contract-matrix.md)

## Validation already run

- For the completed hazard-context checkpoint:
  `cmd /c node --experimental-strip-types --experimental-specifier-resolution=node scripts/aerospaceHazardContextConsumerPacketRegression.mjs` passed from `app/client`.
  `python -m pytest app/server/tests/test_gpsjam_contracts.py -q` passed.
  `python -m pytest app/server/tests/test_ourairports_reference_contracts.py -q` passed.
  `python -m pytest app/server/tests/test_ncei_space_weather_portal_contracts.py -q` passed.
  `python -m pytest app/server/tests/test_swpc_contracts.py app/server/tests/test_cneos_contracts.py app/server/tests/test_opensky_contracts.py app/server/tests/test_aviation_weather_contracts.py app/server/tests/test_faa_nas_status_contracts.py -q` passed.
  `python -m compileall app/server/src` passed.
  From `app/client`, `cmd /c npm.cmd run lint` passed.
  From `app/client`, `cmd /c npm.cmd run build` passed.
  `python scripts/alerts_ledger.py --json` passed.
- Browser smoke status:
  `python app/server/tests/run_playwright_smoke.py aerospace` did not reach app assertions on this host.
  It failed before launch with `spawn EPERM` and the runner classified it as `windows-playwright-launch-permission` / `windows-browser-launch-permission`.
  Treat that as a host launcher blocker, not an aerospace assertion failure.

## Known blockers or caveats

- Prepared smoke is not executed smoke.
  Aerospace has extensive prepared assertion coverage, but executed browser workflow evidence is still blocked locally by the Windows Chromium launch-permission boundary.
- Source-readiness and source-health posture are intentionally bounded.
  These helpers are trust/accounting aids, not operational verdicts.
- No-intent and no-causation guardrails are mandatory across the stack.
  Aerospace helpers must not imply:
  flight intent,
  target behavior,
  GPS/radio/satellite failure proof,
  route impact,
  safety conclusion,
  threat,
  causation,
  or action need.
- The hazard-context consumer packet must keep these distinct:
  GPSJam GNSS context,
  NWS public weather alerts,
  NOAA nowCOAST map-layer metadata,
  AWC aviation weather,
  FAA NAS operational status,
  OpenSky comparison,
  SWPC current advisories,
  NCEI archive metadata.

## What the next AI should do first

- Read:
  [aerospace-workflow-validation.md](/C:/Users/mike/11Writer/app/docs/aerospace-workflow-validation.md)
  [aerospace-workflow-evidence-ledger.md](/C:/Users/mike/11Writer/app/docs/aerospace-workflow-evidence-ledger.md)
  and the newest top entries in [aerospace-ai.md](/C:/Users/mike/11Writer/app/docs/agent-progress/aerospace-ai.md).
- If working on browser workflow truth, first solve or route the Playwright Windows launcher blocker instead of changing aerospace assertions blindly.
- If working with Spatial AI:
  consume `aerospaceHazardContextConsumerPacket` and `aerospaceFusionSnapshotInput` as bounded domain inputs, not as unified source truth.
- If working with Reporting AI:
  start from:
  `aerospaceReportBriefPackage`,
  `aerospaceSelectedTargetOperationalQuestionPacket`,
  `aerospaceCurrentAwarenessDigest`,
  `aerospaceReportingHandoffContract`,
  `aerospaceQuestionBriefingPacket`,
  and the new hazard-context consumer packet.
- If working with Platform AI:
  focus on smoke execution truth, regression ergonomics, and metadata/export consistency rather than opening new source families.
- If working with Connect AI:
  treat `windows-playwright-launch-permission` as the first blocker before reclassifying any aerospace smoke failure as a product bug.

## What not to break

- Do not collapse observed, advisory, contextual, archival, derived, and validation/accounting surfaces into one authority layer.
- Do not turn NWS Alerts into aviation operational status.
- Do not turn nowCOAST layer metadata into alert truth or route guidance.
- Do not turn GPSJam into outage certainty, attribution, or target-specific effect.
- Do not remove the prepared-versus-executed smoke distinction.
- Do not add another large aerospace panel for this completed slice unless Phase 3 explicitly changes the scope.
- Do not weaken the explicit does-not-prove and guardrail lines in the reporting/export helpers.

## Phase 3 relevance

- For Spatial AI:
  aerospace now exposes a stable bounded hazard-context packet that can be consumed alongside broader source-fusion work without pretending GNSS, public alerts, and map layers are the same thing.
- For Reporting AI:
  the aerospace reporting stack is already deep; the right Phase 3 move is careful consolidation and use of the existing packet/brief/digest/handoff surfaces, not more renamed wrappers without a clear reduction in complexity.
- For Platform AI:
  the immediate repo truth is that aerospace validation is strong at regression/build/contract level, but executed browser smoke evidence is still blocked by host launch permissions.
- For Connect AI:
  if Phase 3 wants end-to-end browser evidence, unblocking Chromium launch on Windows is higher leverage than changing aerospace business logic.
