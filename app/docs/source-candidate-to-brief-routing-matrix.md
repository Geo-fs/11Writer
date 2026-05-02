# Source Candidate-To-Brief Routing Matrix

This matrix gives Manager AI and Gather AI one compact routing surface for surviving Wonder, Atlas, and source-discovery leads.

Use it to answer:

- which candidate should stay candidate-only
- which candidate can move toward a Gather brief
- which lane should review it first
- what evidence must exist before a quick-assign packet is allowed

Status rule:

- candidate discovery is not implementation proof
- source-discovery runtime evidence is not source approval
- Wonder OSINT Framework audit artifacts are research input only
- Atlas Wave/Source Discovery work is runtime/governance input only unless a source slice is separately implemented in repo code

Related docs:

- [osint-framework-intake-routing-memo.md](/C:/Users/mike/11Writer/app/docs/osint-framework-intake-routing-memo.md)
- [source-discovery-reputation-governance-packet.md](/C:/Users/mike/11Writer/app/docs/source-discovery-reputation-governance-packet.md)
- [source-assignment-board.md](/C:/Users/mike/11Writer/app/docs/source-assignment-board.md)
- [source-prompt-index.md](/C:/Users/mike/11Writer/app/docs/source-prompt-index.md)
- [webcam-global-camera-candidate-batch-2026-05.md](/C:/Users/mike/11Writer/app/docs/webcam-global-camera-candidate-batch-2026-05.md)

## Routing Matrix

| Lead class | Example provenance | Current classification | Target lane | Next allowed artifact | Minimum missing evidence | Hold/reject trigger |
| --- | --- | --- | --- | --- | --- | --- |
| official/public feed lead | Wonder audit entry with a clearly machine-readable public advisory or press feed | `Data AI feed candidate` | `data` | bounded endpoint-review note, then Gather brief | pinned official docs URL, pinned machine endpoint, no-auth/no-signup confirmation, evidence basis, caveats | signup, browser-only flow, no stable machine endpoint |
| official environmental/hazard lead | Wonder or source-discovery lead pointing to a public warning, hazard, seismic, hydrology, or weather authority | `Geospatial source candidate` | `geospatial` | bounded endpoint-review note, then Gather brief | pinned official docs URL, pinned machine endpoint, owner recommendation, source mode expectation, export metadata expectation | HTML-only page, scraping requirement, hidden auth |
| official marine/coastal/waterway lead | source-discovery or catalog lead for coastal, river, flood, buoy, or water-quality context | `Marine source/context candidate` | `marine` | bounded endpoint-review note, then Gather brief | official docs URL, machine endpoint, evidence basis, marine caveats, source-health expectation | tokenized download path, unstable rotating endpoint, registration |
| aviation/space/reference lead | Wonder or source-discovery lead for airport, aviation, airspace, ash, NEO, space-weather, or bounded aerospace reference context | `Aerospace source/reference candidate` | `aerospace` | bounded endpoint-review note, then Gather brief | pinned endpoint, evidence basis, source-health posture, export metadata expectation | interactive viewer dependence, no reusable machine interface |
| transport/camera/endpoint lead | source-discovery or webcam candidate batch entry with public camera or transport endpoint evidence | `Features/Webcam candidate` | `features-webcam` | candidate endpoint report or graduation-plan note | direct machine endpoint, media posture clarity, inactive lifecycle posture, source-ops caveats | API key, signup, scraping, tokenized viewer dependency |
| discovery/runtime/platform lead | Atlas or source-discovery backend/runtime surface such as memory, health, bounded expand, scheduler tick, or Wave Monitor integration | `Connect runtime review` | `connect` | runtime-boundary note or release-readiness note | explicit route/runtime proof, ownership boundary, non-promotion caveat | any attempt to treat runtime evidence as source approval |
| grouped candidate bucket with plausible source value but no pinned endpoint yet | Wonder `candidate-source-packet` or `candidate-connector-after-endpoint-review` bucket | `Gather brief-needed` | `gather` | brief-needed memo or endpoint pinning queue | source identity, probable owner, likely evidence basis, likely no-auth posture, duplicate check | endpoint still too vague after review |
| directory, catalog, or mixed-source discovery surface | Wonder `review-directory-candidate` bucket | `hold` | `gather` | none beyond routing note | one downstream endpoint must be isolated first | stays a directory, not a reusable source |
| blocked or ambiguous access lead | Wonder `hold-unreachable-or-blocked-check-needed`, held webcam candidate, or blocked registry lead | `rejected` or `hold` | `gather` | hold/reject note only | material change in provider posture | login, key, CAPTCHA, request form, unstable access |
| socially or operationally unsafe lead | any lead whose likely first use would imply targeting, wrongdoing, evasion, surveillance escalation, or access-control bypass | `unsafe/out-of-scope` | `gather` | reject note only | none; route closed | unsafe use profile or policy conflict |

## Minimum Evidence Before A Quick-Assign Packet

No candidate may become a quick-assign packet unless all of this is explicit:

- official docs URL
- machine endpoint
- no-auth/no-signup status
- source owner
- evidence basis
- source mode expectation
- caveats
- export metadata expectation
- do-not-do list

Recommended additional evidence before packeting:

- duplicate check against implemented and briefed sources
- source-health expectation
- fixture-first strategy
- first slice bounded tightly enough to avoid family sprawl

## Current Candidate Notes

- Wonder OSINT Framework audit artifacts:
  - strongest use is candidate bucketing and endpoint-review prioritization
  - weakest use is direct implementation routing
- Atlas Source Discovery / Wave Monitor:
  - strongest use is runtime-boundary and governance planning
  - weakest use is source approval or validation proof
- Global webcam camera batch:
  - strongest use is Features/Webcam candidate endpoint review
  - weakest use is activation, validation, or scheduling
- Batch 7 static/reference backlog:
  - strongest use is narrow geospatial reference slicing
  - weakest use is live hazard, navigation, legal-boundary, or impact claims

## Do-Not-Do Summary

- do not turn candidate routing into automatic briefing
- do not treat runtime routes as source truth
- do not treat Wonder or Atlas artifacts as ownership proof
- do not promote candidate-only webcam records into activation or validation
- do not promote static/reference leads into live-hazard or legal truth
