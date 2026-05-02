# Phase 2 Next Biggest Wins Packet

This packet gives Manager AI one compact planning surface for the next three high-value controlled-agent handoffs per lane without reopening long progress threads or older source-batch docs.

Use it to answer:

- what the next three biggest safe wins are per controlled agent
- whether the next step is a source build, workflow hardening pass, consumer follow-on, or governance sweep
- what caveats must survive the handoff
- which items are blocked by validation risk versus implementation risk

Status rule:

- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md) remains the source-status truth.
- [source-validation-status.md](/C:/Users/mike/11Writer/app/docs/source-validation-status.md) remains the validation-traceability truth.
- Atlas and Wonder remain peer or user-directed input only.
- Source Discovery runtime, Wave LLM runtime, Browser Use guidance, Atlas Source Discovery Ten-Step notes, and Wonder macOS/plugin/connector planning are planning and runtime-boundary input here, not source-validation proof.

## Global Rules

- Keep `implemented`, `contract-tested`, `workflow-validated`, and `fully validated` distinct.
- Do not treat helper packages, review queues, runtime status endpoints, scheduler compatibility helpers, Browser Use guidance, or peer research as source-validation proof.
- Keep source-health, evidence basis, caveats, and no-harmful-use boundaries explicit in every handoff.
- Prefer bounded follow-on work over opening multiple fresh lanes when one lane is already partially implemented.

## Connect AI

| Rank | Source or workflow id | First safe slice | Why it matters now | Source or evidence caveats | Validation or status risk | Handoff type | Do-not-do boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `repo-wide-validation-checkpoint` | rerun targeted compile, lint, build, smoke, alerts, ownership-scan, and validation snapshot after the current wave stabilizes | This is the fastest way to keep status docs honest after multiple agent completions and after the latest runtime-boundary sweep has already landed. | Validation truth must stay machine-specific where Browser or Playwright launch is host-bound. | `medium` because green checkpoints can still hide mixed-worktree collision risk. | `validation sweep` | Do not convert one host's green run into universal workflow validation. |
| 2 | `source-discovery-warning-reduction` | reduce the remaining noisy Source Discovery and Wave Monitor warning classes without changing runtime meaning | The runtime-boundary sweep is already complete, so the next Connect value is making validation output easier to trust and review. | Source Discovery runtime remains candidate and review infrastructure only. | `medium` because warning cleanup can accidentally drift into semantic changes if not bounded. | `runtime hardening` | Do not imply hidden polling, automatic approval, or live scheduler proof. |
| 3 | `browser-verification-guidance-adoption` | route rendered-page verification through Browser Use guidance and security checklist in repo docs | Wonder's Browser guidance is useful only if controlled lanes actually route verification work through it safely. | Browser guidance is verification posture only, not source truth. | `medium` because browser verification can drift into unsafe rendered-content trust. | `governance rollout` | Do not treat rendered pages, browser text, or visual reachability as validation by themselves. |

## Data AI

| Rank | Source or workflow id | First safe slice | Why it matters now | Source or evidence caveats | Validation or status risk | Handoff type | Do-not-do boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `data-ai-source-intelligence` | keep the inspector card metadata-only and record one bounded workflow or export note over readiness, review, and review-queue surfaces | The client-light consumer now exists, so the clean next win is making its bounded workflow posture explicit instead of reopening raw feed intake. | The card is metadata only and must not echo URL-bearing lines, hostile feed text, or implied scores. | `high` because review metadata can be mistaken for source credibility, severity, or action guidance. | `workflow follow-on` | Do not treat card rows as source truth, priority truth, or required-action output. |
| 2 | `data-ai-source-family-review-queue` | keep `GET /api/feeds/data-ai/source-families/review-queue` metadata-only and align it with the existing Source Intelligence card and export-safe lines | The queue is already implemented, so the next larger Data workflow is coherence and bounded review visibility rather than another raw connector. | Review queue lines are metadata only and must not echo free-form hostile feed text. | `high` because review metadata can be mistaken for source credibility or action guidance. | `workflow follow-on` | Do not treat queue items as source truth, priority truth, or required-action output. |
| 3 | `propublica` or `global-voices` | one bounded investigations or civic-reporting feed family only after the current metadata-only consumer path stays stable | If Manager wants a fresh Data build after the implemented waves settle, these remain the cleanest bounded next packets. | Investigative and civic reporting stays contextual only. | `high` because quoted text, advocacy language, and duplicate-story handling can drift. | `source build` | Do not convert reporting into wrongdoing proof, field confirmation, or operational guidance. |

## Geospatial AI

| Rank | Source or workflow id | First safe slice | Why it matters now | Source or evidence caveats | Validation or status risk | Handoff type | Do-not-do boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `bc-wildfire-datamart` | one bounded consumer or workflow note over the implemented fire-weather context slice | This is already backend-first and gives fast value without opening a second large geospatial lane. | BCWS slice is fire-weather context only, not wildfire incident or evacuation truth. | `medium` because consumer drift could overstate fire-weather semantics. | `consumer follow-on` | Do not turn fire-weather context into incident, perimeter, evacuation, or damage claims. |
| 2 | `meteoswiss-open-data` | one bounded consumer or workflow note over the implemented SwissMetNet station-context slice | The backend-first slice now exists, so the next win is explicit consumer/workflow evidence rather than reassigning it as fresh source intake. | Keep it narrow and observation-focused. | `medium` because catalog sprawl and observation-overclaim drift remain the main risks. | `consumer follow-on` | Do not ingest the full product catalog or widen into multi-family weather/platform work. |
| 3 | `canada-cap-alerts` | one public CAP directory family only | Strong official advisory value with good fit for environmental alert context. | CAP remains advisory and contextual only. | `medium` because alert wording and geometry handling can drift. | `source build` | Do not turn alert text into impact, damage, or certainty claims. |

## Marine AI

| Rank | Source or workflow id | First safe slice | Why it matters now | Source or evidence caveats | Validation or status risk | Handoff type | Do-not-do boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `france-vigicrues-hydrometry` | add the first bounded consumer or explicit workflow note over the backend-only hydrometry slice | The lane is already active, so finishing it is higher value than opening a second marine source immediately. | River and station values remain hydrology context only. | `medium` because source-health and consumer-path evidence are still missing. | `consumer follow-on` | Do not infer inundation, impact, safety, causation, or action guidance from station values alone. |
| 2 | `netherlands-rws-waterinfo` | one bounded marine-local consumer, helper, or workflow note over the implemented metadata plus latest water-level slice | The backend-first WaterWebservices slice now exists, so the next value is bounded marine consumption/workflow evidence rather than another raw source build. | Waterinfo is approved only for the narrow POST-based slice. | `medium` because widening into portal or historical families would break the approval basis. | `consumer follow-on` | Do not use viewer pages, broaden into portal ingestion, or infer impact from water-level values alone. |
| 3 | `marine-source-health-hardening` | explicit `unavailable` and selective `degraded` workflow truth across active marine context families | This closes the remaining gap between strong contract evidence and fuller workflow confidence. | These are workflow-supporting semantics, not live-source proof. | `medium` because over-promotion from helper evidence is easy. | `workflow hardening` | Do not promote marine sources beyond recorded workflow evidence. |

## Aerospace AI

| Rank | Source or workflow id | First safe slice | Why it matters now | Source or evidence caveats | Validation or status risk | Handoff type | Do-not-do boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `aerospaceContextReviewQueue` | execute prepared smoke on a Windows host where Playwright can launch and record the review-queue/export-bundle evidence path | The review queue and export bundle now exist, so the cleanest next move is explicit workflow evidence instead of more helper surface. | Prepared smoke is not executed smoke. | `high` because current host limits can be misread as workflow success or failure. | `workflow hardening` | Do not collapse prepared assertions into executed workflow validation. |
| 2 | `aerospaceWorkflowReadinessPackage` | keep the readiness package aligned with the review queue and existing export profiles while rerunning smoke on a launch-capable host | The package is already implemented and is still part of the bridge from contract-tested to explicit workflow evidence. | Prepared smoke is not executed smoke. | `high` because current host limits can be misread as workflow success or failure. | `workflow hardening` | Do not collapse prepared assertions into executed workflow validation. |
| 3 | `aviationWeatherContext-workflow` | rerun AWC, FAA NAS, CNEOS, SWPC, and OpenSky smoke/export checks once browser launch is available | Aerospace already has the deepest contract-tested source stack, so the highest value is workflow closure. | Observed, forecast, archive, and reference contexts must stay separate. | `high` because browser-smoke absence is the last major gap. | `workflow hardening` | Do not reopen fresh aerospace source work just to avoid the validation gap. |

## Features/Webcam AI

| Rank | Source or workflow id | First safe slice | Why it matters now | Source or evidence caveats | Validation or status risk | Handoff type | Do-not-do boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `finland-digitraffic` | one bounded consumer or status-classification follow-on over the implemented backend slice | This is the cleanest next operational-context win without opening another large camera lane. | Keep road-weather scope separate from cameras or transport analytics sprawl. | `medium` because there is still no workflow validation record. | `consumer follow-on` | Do not widen into full transport analytics or cross-mode feed fusion. |
| 2 | `sandbox-candidate-review-burden-summary` | keep the review-burden, missing-evidence, source-health-expectation, and next-review-priority summary aligned and bounded | This is the strongest newer source-ops workflow surface now that multiple camera candidates are sandbox-importable. | These are source-ops helpers, not source proof. | `medium` because helper evidence can be mistaken for activation or validation. | `workflow hardening` | Do not treat source-ops review metadata as source truth, activation proof, or live validation. |
| 3 | `sandbox-camera-candidate-set` | keep NSW, Quebec, Maryland, and Fingal at `candidate-sandbox-importable` while adding only bounded source-health or review-burden follow-ons | This preserves momentum on the candidate set without unsafe activation drift. | Sandbox-importable is still candidate-only. | `high` because candidate posture is easy to over-promote. | `candidate follow-on` | Do not activate, schedule, validate, or imply live ingest for sandbox-only candidates. |

## Gather AI

| Rank | Source or workflow id | First safe slice | Why it matters now | Source or evidence caveats | Validation or status risk | Handoff type | Do-not-do boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `status-reconciliation-after-each-wave` | keep board, validation, workflow, prompt, and routing docs synchronized after each controlled-agent completion | Multiple lanes are moving faster than the docs, so stale status is now one of the main failure modes. | Gather owns truth reconciliation, not implementation proof. | `high` because mixed status surfaces can misroute whole waves. | `governance` | Do not promote helper or peer evidence into workflow validation. |
| 2 | `held-source-verification-queue` | verify one bounded held source at a time, starting from the assignment board and packet docs | This is the cleanest way to keep the next source wave moving without opening vague prompts. | Held verification is not implementation or approval by itself. | `medium` because endpoint pinning can be mistaken for broader product-family approval. | `verification memo` | Do not widen a narrow verification memo into a broad source-family approval. |
| 3 | `peer-input-governance` | keep Atlas, Wonder, Browser Use guidance, and Source Discovery runtime work represented as peer/runtime input only | Peer contributions are now materially useful, but they are easy to over-promote. | Peer and user-directed work is not Manager-owned validation proof. | `high` because governance drift can reclassify peer input as implementation truth. | `governance` | Do not convert peer docs, audits, or runtime notes into source-validation proof. |

## Immediate Manager Order

If Manager AI wants the fastest next larger wins without reopening prompt archaeology:

1. `Connect`: `repo-wide-validation-checkpoint`
2. `Data`: `data-ai-source-intelligence`
3. `Geospatial`: `bc-wildfire-datamart` or `meteoswiss-open-data` consumer/workflow follow-on
4. `Marine`: `france-vigicrues-hydrometry` first consumer or `netherlands-rws-waterinfo` bounded helper follow-on
5. `Aerospace`: `aerospaceContextReviewQueue` smoke execution on a launch-capable Windows host
6. `Features/Webcam`: `sandbox-candidate-review-burden-summary`
7. `Gather`: `status-reconciliation-after-each-wave`

## Peer Input Note

- Atlas Source Discovery runtime review remains peer/runtime input only unless Connect separately validates the current runtime boundaries.
- Wonder Browser Use and browser-security guidance remain verification guidance only and should inform agent behavior, not source-validation promotion.
- Wonder macOS/plugin/connector planning remains peer planning input only and should inform routing boundaries, not implementation or source-validation promotion.
