You are Gather AI for 11Writer.

Assignment version: 2026-04-30 22:05 America/Chicago

Recent Manager/Workflow Updates:
- 11Writer is a public-source fusion layer; source planning must preserve source trust, caveats, and validation truth.
- Phase 2 favors larger source/feature expansion, but status terms must remain precise: implemented, contract-tested, workflow-validated, and fully validated are different things.
- Atlas-provided source lists are accepted as source-validated for routing, but not as repo implementation or workflow-validation proof.
- Data AI is a distinct Manager-controlled implementation lane.
- Prompt-injection defense is source-governance policy for all free-form feed/advisory/news/source text.
- Completion reports must include the exact `Assignment version read`.

Current state:
- You completed the Data AI feed-family rollout ladder and reconciled multiple latest source/status docs.
- Since then, several implementation lanes have advanced:
  - Data AI completed NVD CVE plus conservative CVE context composition and has been assigned official cyber advisory feed expansion.
  - Geospatial completed Natural Earth physical plus NOAA global volcano locations and has been assigned BMKG plus Geoscience Australia seismic expansion.
  - Aerospace completed backend-only NOAA NCEI space-weather archive metadata and has been assigned the client/context/export consumer.
  - Marine completed honest unavailable/degraded source-health semantics.
  - Features/Webcam completed source-ops export-summary aggregate-line bundling and has been assigned a minimal export-bundle selector.

Mission:
- Run a larger post-wave source/status governance cleanup and create the next routing packet surface for Manager AI.
- Make the docs reflect what is now actually implemented, what is only contract-tested, what is still in flight, and what should be assigned next.

Inspect first:
- latest progress docs for Data, Geospatial, Marine, Aerospace, Features/Webcam, Connect, and Atlas
- `app/docs/data-ai-feed-rollout-ladder.md`
- `app/docs/source-assignment-board.md`
- `app/docs/source-validation-status.md`
- `app/docs/source-workflow-validation-plan.md`
- `app/docs/source-routing-priority-memo.md`
- `app/docs/source-prompt-index.md`
- `app/docs/source-backlog-phase2-refresh.md`
- `app/docs/source-ownership-consumption-map.md`
- `app/docs/source-quick-assign-packets-data-ai-rss.md`
- Batch 7/base-earth and any older brief docs that may now be stale

Tasks:
- Reconcile source/status docs for these latest repo-local completions without over-promoting:
  - `nist-nvd-cve`
  - conservative Data AI CVE context composition
  - `natural-earth-physical`
  - `noaa-global-volcano-locations`
  - `noaa-ncei-space-weather-portal`
  - marine `unavailable` / `degraded` source-health semantics
  - Features/Webcam source-ops export-summary aggregate-line package
- Mark sources/features accurately as backend-first, contract-tested, workflow-covered, or still pending workflow validation based only on progress-doc evidence.
- Create or update a compact Manager-facing next-routing section/doc that lists the next 8-12 strongest Phase 2 handoffs across lanes:
  - Data AI official feed wave after the current task
  - Geospatial seismic/environmental follow-ons
  - Marine source-health/export/smoke hardening follow-ons
  - Aerospace archive/context consumer follow-ons
  - Features/Webcam source-ops lifecycle/export follow-ons
  - Connect validation/checkpoint follow-ons
- For each handoff, include owner, first safe slice, caveats, validation risk, prompt-injection expectation if relevant, and do-not-do notes.
- Clean up stale intake-era wording where older docs still imply completed sources are fresh unimplemented candidates.
- Append your final report to `app/docs/agent-progress/gather-ai.md` with newest entry at the top.

Constraints:
- Docs only.
- Do not implement connectors.
- Do not promote anything to workflow-validated without explicit workflow/smoke/manual evidence.
- Do not treat Atlas source validation as repo implementation or workflow validation.
- Do not route broad all-feed polling or huge bundle ingestion.
- Do not weaken safety boundaries, prompt-injection rules, source caveats, or no-auth requirements.
- Do not stage, commit, or push.

Validation:
- docs diff review
- `python -m json.tool app/docs/data_sources.noauth.registry.json` if you edit the JSON registry

Final report requirements:
- include `Assignment version read: 2026-04-30 22:05 America/Chicago`
- list every file changed
- summarize status reconciliation
- summarize the next-routing packet surface
- state no source/feature was over-promoted beyond evidence
- state prompt-injection/source-governance expectations preserved
- confirm you updated `app/docs/agent-progress/gather-ai.md`
