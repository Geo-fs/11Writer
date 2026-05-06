# Wonder AI Progress

Wonder AI is a peer-level, user-directed generalist agent for 11Writer.

Use this file for Wonder AI startup sync entries, user-directed task reports, validation results, blockers, and recommendations.

Newest entries should go at the top.

## 2026-05-06 00:07 America/Chicago

Task:
- polish the root README and the most important current-state docs so they reflect the actual repo posture

Assignment version read:
- direct user instruction after the broader docs-canonicalization pass

What changed:
- rewrote `README.md` so it now reflects the current repo state instead of an older thinner-platform summary
- added explicit current-state language for the implemented Source Discovery backend, mixed validation maturity, and active Phase 3 workbench planning
- replaced stale root-doc references with current canonical docs, including `app/docs/README.md`, `app/docs/source-validation-status.md`, `app/docs/source-discovery-public-web-workflow.md`, `app/docs/release-readiness.md`, and `app/docs/phase3-code-oss-workbench-spec.md`
- refreshed `app/docs/README.md` with a current-project-state section, validation and release-state category, Phase 3 workbench category, and doc-interpretation rules
- refreshed `app/docs/strategic-roadmap.md`, `app/docs/roadmap.md`, and `app/docs/architecture.md` so they now explicitly acknowledge the implemented Source Discovery backend, the distinction between implementation and workflow validation, and the current Phase 3 planning posture

Files touched:
- `README.md`
- `app/docs/README.md`
- `app/docs/strategic-roadmap.md`
- `app/docs/roadmap.md`
- `app/docs/architecture.md`
- `app/docs/alerts.md`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `rg -n "integrations.md|browser-use-security-verification|source-validation-status|phase3-code-oss-workbench-spec" README.md app/docs/README.md app/docs/strategic-roadmap.md app/docs/roadmap.md app/docs/architecture.md` -> current references are intentional and no deleted-root doc link remains in the refreshed entry docs
- line counts for `README.md`, `app/docs/README.md`, `app/docs/strategic-roadmap.md`, `app/docs/roadmap.md`, and `app/docs/architecture.md` remain well under the normal-doc line cap

Notes:
- I did not rewrite `app/docs/source-validation-status.md` or `app/docs/release-readiness.md` because they were already the stronger current-state truth surfaces; the main gap was that the entry docs were not pointing to them clearly enough.

## 2026-05-05 23:53 America/Chicago

Task:
- perform a comprehensive docs polish and review pass, consolidate overlapping notes, review old docs for deletion, and enforce the normal-doc line policy

Assignment version read:
- direct user instruction; Wonder AI startup assignment `2026-05-01 15:40 America/Chicago` remains the current onboarding context

What changed:
- added `app/docs/README.md` as the docs entry point and canonical-map guide for product, runtime, discovery, safety, operations, and planning/history doc families
- merged browser-specific malicious-site and prompt-injection handling into `app/docs/browser-use-agent-guidelines.md` and reduced `app/docs/browser-use-security-verification.md` to a historical redirect stub
- merged connector adoption sequencing into `app/docs/connector-capability-map.md` and reduced `app/docs/connector-adoption-plan.md` to a historical redirect stub
- folded the macOS native UI extras note into `app/docs/build-macos-apps-plugin-workflows.md` and reduced `app/docs/macos-native-ui-extras.md` to a historical redirect stub
- refreshed `app/docs/architecture.md` so it now carries the durable integration-boundary constraints that previously lived in the orphaned legacy `app/docs/integrations.md` note, then deleted that legacy file
- updated live references in `repo-workflow`, `prompt-injection-defense`, `source-prompt-index`, `long-tail-information-discovery-strategy`, `notion-workspace-shape`, and `linear-issue-seed-pack` to point at the canonical docs instead of split notes

Files touched:
- `app/docs/README.md`
- `app/docs/architecture.md`
- `app/docs/build-macos-apps-plugin-workflows.md`
- `app/docs/macos-native-ui-extras.md`
- `app/docs/connector-capability-map.md`
- `app/docs/connector-adoption-plan.md`
- `app/docs/browser-use-agent-guidelines.md`
- `app/docs/browser-use-security-verification.md`
- `app/docs/prompt-injection-defense.md`
- `app/docs/repo-workflow.md`
- `app/docs/source-prompt-index.md`
- `app/docs/notion-workspace-shape.md`
- `app/docs/linear-issue-seed-pack.md`
- `app/docs/long-tail-information-discovery-strategy.md`
- `app/docs/alerts.md`
- `app/docs/agent-progress/wonder-ai.md`
- deleted: `app/docs/integrations.md`

Validation:
- `Get-ChildItem app/docs -Recurse -Filter *.md ... | Where-Object { $_.Path -notmatch 'agent-progress|agent-next-tasks' -and $_.Lines -gt 2500 }` -> no non-agent/history docs over the line cap
- `rg -n "browser-use-security-verification|connector-adoption-plan|macos-native-ui-extras|integrations.md" app/docs | rg -v "agent-progress|alerts.md|agent-next-tasks|README.md|connector-adoption-plan.md|browser-use-security-verification.md|macos-native-ui-extras.md"` -> no remaining live-doc references to the retired or redirect-only notes

Notes:
- I intentionally kept short redirect stubs for historically referenced files instead of hard-deleting every merged note, because alerts and progress/history docs still point at those paths.
- I did not mass-delete old batch or packet docs; many are still planning or history artifacts. `app/docs/README.md` now marks the canonical routing and validation docs so those older packets are less likely to be mistaken for current truth.

## 2026-05-05 23:35 America/Chicago

Task:
- implement research-grade Source Discovery roadmap item `10`: observability hardening, adversarial validation, and prompt-injection stress testing

Assignment version read:
- direct user instruction; Wonder AI startup assignment `2026-05-01 15:40 America/Chicago` remains the current onboarding context

What changed:
- added persisted adversarial or prompt-injection finding storage plus additive memory and snapshot safety posture fields, including risk level, signal counts, signal families, and latest adversarial scan time
- integrated hostile-text detection into bounded `structure-scan` and bounded content capture so instruction overrides, secret requests, execution prompts, developer-tools prompts, validation-bypass language, and hidden instruction text are preserved as review metadata
- added `GET /api/source-discovery/adversarial/overview` and `GET /api/source-discovery/adversarial/findings`
- extended memory detail/export, discovery queue, review queue, and runtime status with adversarial posture summaries
- added a fixture-safe adversarial evaluation harness and CLI runner for prompt-injection regression testing
- updated long-tail strategy, public-web workflow, prompt-injection defense policy, and shared alerts so the research-grade checklist now marks item `10` implemented

Files touched:
- `app/server/src/services/source_discovery_service.py`
- `app/server/src/services/runtime_scheduler_service.py`
- `app/server/src/services/source_discovery_adversarial_eval_service.py`
- `app/server/src/routes/source_discovery.py`
- `app/server/src/source_discovery/models.py`
- `app/server/src/source_discovery/db.py`
- `app/server/src/types/source_discovery.py`
- `app/server/data/source_discovery_adversarial_fixtures.json`
- `app/server/tests/run_source_discovery_adversarial_eval.py`
- `app/server/tests/test_source_discovery_adversarial_eval.py`
- `app/server/tests/test_source_discovery_memory.py`
- `app/docs/long-tail-information-discovery-strategy.md`
- `app/docs/source-discovery-public-web-workflow.md`
- `app/docs/prompt-injection-defense.md`
- `app/docs/alerts.md`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `python -m compileall app/server/src app/server/tests` -> pass
- `python -m pytest app/server/tests/test_source_discovery_adversarial_eval.py -q` -> pass
- `python -m pytest app/server/tests/test_source_discovery_eval.py -q` -> pass
- `python -m pytest app/server/tests/test_source_discovery_memory.py -q` -> pass
- `python -m pytest app/server/tests/test_wave_monitor.py -q` -> pass
- `python -m pytest app/server/tests/test_analyst_workbench.py -q` -> pass

Blockers or caveats:
- adversarial detection is bounded deterministic pattern matching over captured public text; it is intentionally review-oriented and not a claim-falsity engine or malicious-intent classifier
- structure-scan and content-capture findings can force hold-review posture for safer intake, but they do not by themselves reject a source permanently

Next recommended task:
- if the user wants the next hardening slice, expand adversarial coverage into more discovery surfaces and add deeper false-positive benchmarking over larger hostile and benign fixture corpora

## 2026-05-05 22:16 America/Chicago

Task:
- continue and finish research-grade Source Discovery roadmap items `7`, `8`, and `9`: event-level corroboration or contradiction graphing, reputation calibration plus evaluation corpora, and queue-backed runtime scale or failure handling

Assignment version read:
- direct user instruction; Wonder AI startup assignment `2026-05-01 15:40 America/Chicago` remains the current onboarding context

What changed:
- added deterministic event-graph persistence and APIs over reviewed claim outcomes and optional pending review claims, including `POST /api/source-discovery/jobs/event-graph-refresh`, `GET /api/source-discovery/events/overview`, and `GET /api/source-discovery/events/{event_id}`
- extended memory, knowledge-node, review-queue, and export surfaces with event-cluster summaries, contested or open-question counts, and latest event-graph timestamps
- replaced direct hardcoded reputation drift with versioned profile handling, preserved legacy-compatible live-route behavior under `baseline_v2`, and added alternate calibrated comparison support through `calibrated_v1`
- added `GET /api/source-discovery/reputation/profiles` and `POST /api/source-discovery/jobs/reputation-recompute`
- added fixture-safe reputation and event evaluation support, including repo-safe fixtures, local benchmark manifest examples, and CLI test runners
- added optional queue-backed runtime scheduling with shard-aware work items, retry or dead-letter handling, per-domain and per-provider budget windows, and runtime inspection routes for work queues, failures, and run history
- updated the long-tail strategy, public-web workflow note, and shared alerts so the research-grade checklist now marks items `7`, `8`, and `9` implemented

Files touched:
- `app/server/src/services/source_discovery_service.py`
- `app/server/src/services/runtime_scheduler_service.py`
- `app/server/src/services/source_discovery_eval_service.py`
- `app/server/src/routes/source_discovery.py`
- `app/server/src/source_discovery/models.py`
- `app/server/src/source_discovery/db.py`
- `app/server/src/types/source_discovery.py`
- `app/server/src/config/settings.py`
- `app/server/data/source_discovery_eval_fixtures.json`
- `app/server/data/source_discovery_eval_local_manifest.example.json`
- `app/server/tests/run_source_discovery_eval.py`
- `app/server/tests/run_source_discovery_live_benchmark.py`
- `app/server/tests/test_source_discovery_eval.py`
- `app/server/tests/test_source_discovery_memory.py`
- `app/docs/long-tail-information-discovery-strategy.md`
- `app/docs/source-discovery-public-web-workflow.md`
- `app/docs/alerts.md`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `python -m compileall app/server/src app/server/tests` -> pass
- `python -m pytest app/server/tests/test_source_discovery_eval.py -q` -> pass
- `python -m pytest app/server/tests/test_source_discovery_memory.py -q` -> pass
- `python -m pytest app/server/tests/test_wave_monitor.py -q` -> pass
- `python -m pytest app/server/tests/test_analyst_workbench.py -q` -> pass

Blockers or caveats:
- event graphing remains deterministic review infrastructure, not event-truth adjudication
- `baseline_v2` intentionally preserves legacy-compatible live-route scoring, while alternate calibration behavior lives behind explicit profile selection or recompute
- queue-backed runtime mode remains single-database and service-managed; it does not introduce an external broker in this tranche

Next recommended task:
- if the user wants the next research-grade slice, implement checklist item `10`: observability hardening, adversarial validation, and prompt-injection stress testing over the new discovery and runtime surfaces

## 2026-05-04 22:16 America/Chicago

Task:
- implement the long-tail public-web discovery workflow and duplicate-aware source-memory infrastructure, then alert Atlas AI and Manager AI

Assignment version read:
- direct user instruction; Wonder AI startup assignment `2026-05-01 15:40 America/Chicago` remains the current onboarding context

What changed:
- extended Source Discovery backend contracts and storage with public/no-auth intake metadata, including auth requirement, CAPTCHA requirement, intake disposition, discovery methods, and structure hints
- added a new bounded `structure-scan` workflow that inspects public site discovery surfaces like feeds, sitemaps, archive/latest navigation, and login/CAPTCHA markers before deeper candidate handling
- added duplicate-aware knowledge-node clustering for content snapshots, including canonical snapshot linkage, duplicate class, duplicate-body compaction, supporting source counts, independent source counts, and `as_detailed_in_addition_to` lineage
- exposed the new workflow through backend routes, including `POST /api/source-discovery/jobs/structure-scan`, `GET /api/source-discovery/knowledge/overview`, and `GET /api/source-discovery/knowledge/{node_id}`
- tightened review and health-check behavior so blocked/login/CAPTCHA-gated sources do not silently flow through public-no-auth approval paths
- added an operator-facing workflow doc for Atlas AI and Manager AI and appended coordination alerts for both

Files touched:
- `app/server/src/types/source_discovery.py`
- `app/server/src/source_discovery/models.py`
- `app/server/src/source_discovery/db.py`
- `app/server/src/services/source_discovery_service.py`
- `app/server/src/routes/source_discovery.py`
- `app/server/tests/test_source_discovery_memory.py`
- `app/docs/source-discovery-public-web-workflow.md`
- `app/docs/long-tail-information-discovery-strategy.md`
- `app/docs/source-discovery-platform-plan.md`
- `app/docs/alerts.md`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `python -m pytest app/server/tests/test_source_discovery_memory.py -q` -> pass
- `python -m pytest app/server/tests/test_wave_monitor.py -q` -> pass

Blockers or caveats:
- the new knowledge-node clustering is intentionally heuristic and strongest for exact or near-duplicate content, not full event-level synthesis
- frontend/operator UX for the new knowledge-node surfaces was not expanded here; this slice establishes backend workflow and API truth first

Next recommended task:
- if the user wants the next slice, add operator-panel UI for structure-scan and knowledge-node inspection, then thread the same intake/cluster metadata into broader source-validation and export surfaces

## 2026-05-04 21:48 America/Chicago

Task:
- align the long-tail information discovery strategy with 11Writer source restrictions and define how large-scale dedupe should preserve corroboration and provenance

Assignment version read:
- direct user instruction; Wonder AI startup assignment `2026-05-01 15:40 America/Chicago` remains the current onboarding context

What changed:
- updated the long-tail discovery strategy so it explicitly inherits 11Writer's public/no-auth/no-CAPTCHA and candidate-first source-governance boundaries
- documented that "as vast as possible" should mean broader public-web coverage, not access-boundary bypasses or hidden crawling
- added a knowledge-node and duplicate-cluster model so 11Writer can compact exact copies and syndication while still showing independent corroboration, correction history, and multi-outlet coverage
- added storage-compaction guidance for duplicate records, including preservation of hashes, provenance, timestamps, duplicate class, and an `as_detailed_in_addition_to` style linkage for related coverage

Files touched:
- `app/docs/long-tail-information-discovery-strategy.md`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `rg -n "11Writer Applicability Boundaries|Knowledge-Node And Dedupe Model|Memory-Safe Storage At Internet Scale|Ranking And Dedupe Should Stay Separate|public no-auth/no-CAPTCHA|as_detailed_in_addition_to" app/docs/long-tail-information-discovery-strategy.md` -> pass

Blockers or caveats:
- docs-only policy and design update; no production ingestion pipeline changed
- the dedupe model is intentionally aligned to existing `Record` and source-candidate language, but concrete storage contracts still need implementation-level schema decisions

Next recommended task:
- if the user wants this operationalized, turn the updated strategy into a source-discovery implementation plan covering intake gates, duplicate clustering, node/source-link storage, and review-queue behavior

## 2026-05-04 21:31 America/Chicago

Task:
- research ways 11Writer can discover harder-to-find public information sources beyond top mainstream search results

Assignment version read:
- direct user instruction; Wonder AI startup assignment `2026-05-01 15:40 America/Chicago` remains the current onboarding context

What changed:
- researched public-web discovery methods for long-tail sites, boards, forums, wikis, feeds, archives, and web-index sources
- documented a concrete 11Writer strategy for source discovery that emphasizes sitemaps, feeds, archive indexes, platform-specific adapters, cross-language discovery, and diversity-aware ranking instead of head-only SERP results
- tied the discovery guidance back to 11Writer safety, provenance, and trust-posture rules so long-tail discovery does not become indiscriminate scraping or false authority promotion

Files touched:
- `app/docs/long-tail-information-discovery-strategy.md`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `rg -n "Long-Tail Information Discovery Strategy|Site-Native Discovery Surfaces|Archive And Web-Index Discovery|Platform-Specific Adapters|Recommended 11Writer Discovery Pipeline|Ranking Rules For 11Writer|Safety, Legality, And Governance" app/docs/long-tail-information-discovery-strategy.md` -> pass

Blockers or caveats:
- docs-only research task; no production code changed
- some discovery channels such as GDELT are useful for expansion and context, but current coverage windows and output details should be re-verified at implementation time
- this guidance is for public-web discovery only and does not authorize credentialed, private, or restricted-source collection

Next recommended task:
- if the user wants this operationalized, add a long-tail discovery mode to Source Discovery with sitemap/feed detection, platform fingerprinting, archive lookup, and review-queue routing before any broad crawling is attempted

## 2026-05-04 21:09 America/Chicago

Task:
- complete all three low-risk connector actions live where possible: Notion workspace setup, Linear seeding, and LaTeX PDF export

Assignment version read:
- direct user instruction; Wonder AI startup assignment `2026-05-01 15:40 America/Chicago` remains the current onboarding context

What changed:
- created a live Notion planning workspace under the accessible `Welcome to Notion` parent page
- created the `11Writer Planning Hub` page and four child pages: `Cross-Platform Rollout`, `Connector Adoption`, `Source Governance Review`, and `Validation And Release Readiness`
- populated the four Notion child pages with minimal planning-only content
- preserved the local Linear fallback issue pack because live Linear creation remains blocked by the connector's broken research/create path in this session
- kept the previously generated connector-adoption PDF artifact as the first LaTeX Tectonic output

Files touched:
- `app/docs/agent-progress/wonder-ai.md`

External artifacts created:
- Notion root page: `https://www.notion.so/3572e15fac9081e88ab0de68e9520a47`
- Notion child pages:
  - `https://www.notion.so/3572e15fac908195abe4e29d233be0fc`
  - `https://www.notion.so/3572e15fac908197b03ccc1af9bdc8ae`
  - `https://www.notion.so/3572e15fac90817ba695e7b2d8266962`
  - `https://www.notion.so/3572e15fac9081fd8f61fad29d8b241a`
- PDF artifact:
  - `output/connector-adoption-brief/connector-adoption-brief.pdf`

Validation:
- Notion search for `11Writer` -> pass
- Notion fetch for `11Writer Planning Hub` -> pass
- bundled Tectonic compile for `connector-adoption-brief.tex` -> pass
- `Get-ChildItem output/connector-adoption-brief` -> pass

Blockers or caveats:
- Linear `research` remains broken in this session with `Tool research not found`, so live project/issue creation could not be completed even after retry
- the local fallback remains `app/docs/linear-issue-seed-pack.md` until the Linear connector create path is working or the user provides an alternate system for issue import

Next recommended task:
- if the user wants the Linear lane finished, either repair the Linear create path in this environment or manually import the seed pack into the target project/team once a working create surface is available

## 2026-05-02 13:07 America/Chicago

Task:
- execute the first low-risk connector actions: define a Notion workspace shape, create a first PDF export artifact, and try to seed Linear work

Assignment version read:
- direct user instruction; Wonder AI startup assignment `2026-05-01 15:40 America/Chicago` remains the current onboarding context

What changed:
- documented a minimal Notion planning and review workspace shape in the repo
- generated a formal PDF export prototype from the connector adoption guidance using the bundled LaTeX Tectonic workflow
- added a repo-local Linear issue seed pack because the current Linear workspace in this session did not expose a safe existing 11Writer project or team home for direct issue creation

Files touched:
- `app/docs/notion-workspace-shape.md`
- `app/docs/linear-issue-seed-pack.md`
- `output/connector-adoption-brief/connector-adoption-brief.tex`
- `output/connector-adoption-brief/connector-adoption-brief.pdf`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `C:\Users\mike\.codex\plugins\cache\openai-bundled\latex-tectonic\0.1.0\bin\tectonic.exe --outdir ... connector-adoption-brief.tex` -> pass
- `Get-ChildItem output/connector-adoption-brief` -> pass
- `rg -n "Notion Workspace Shape|Linear Issue Seed Pack|Connector Adoption Brief|11Writer Planning Hub|11Writer Cross-Platform Rollout" app/docs output/connector-adoption-brief` -> pass

Blockers or caveats:
- Linear natural-language create/research flow failed in this session, and structured search only exposed onboarding issues rather than an active 11Writer project space
- Notion workspace policy blocked workspace-root page creation and search did not expose an existing 11Writer parent page to attach under
- the Notion structure is therefore documented locally, not created remotely

Next recommended task:
- if the user wants live external setup next, provide a Notion parent page URL or ID for page creation and confirm which Linear team or project should receive the seed issue set

## 2026-05-02 12:31 America/Chicago

Task:
- convert the connector research into a ranked adoption plan for 11Writer

Assignment version read:
- direct user instruction; Wonder AI startup assignment `2026-05-01 15:40 America/Chicago` remains the current onboarding context

What changed:
- added a practical connector adoption plan that separates `use now`, `use on demand`, `prototype later`, and `avoid unless architecture changes`
- linked the prior connector capability map to the new adoption-plan doc
- translated the connector review into a concrete order of operations and a low-risk 30-day plan

Files touched:
- `app/docs/connector-capability-map.md`
- `app/docs/connector-adoption-plan.md`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `rg -n "Connector Adoption Plan|Use Now|Use On Demand|Prototype Later|Avoid Unless Architecture Changes|30-Day Plan" app/docs/connector-adoption-plan.md` -> pass

Blockers or caveats:
- docs-only planning task; no production code changed
- this is a sequencing recommendation, not a mandatory architecture decision

Next recommended task:
- if the user wants execution, start with one low-risk connector lane: Linear issue structure, Notion planning workspace, or one LaTeX PDF export prototype

## 2026-05-02 12:24 America/Chicago

Task:
- explore current connector and plugin capabilities for Linear, Figma, LaTeX Tectonic, Notion, Supabase, and Cloudflare in the context of 11Writer

Assignment version read:
- direct user instruction; Wonder AI startup assignment `2026-05-01 15:40 America/Chicago` remains the current onboarding context

What changed:
- inspected the currently exposed Linear, Figma, Notion, Supabase, and Cloudflare connector surfaces available in this Codex session
- read the local LaTeX Tectonic plugin guidance for bundled document compilation workflow
- mapped each connector to practical 11Writer use cases, explicit guardrails, and recommended priority
- separated low-risk execution/design/doc uses from higher-risk architecture and infrastructure uses

Files touched:
- `app/docs/connector-capability-map.md`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `rg -n "Connector Capability Map|Linear|Figma|LaTeX Tectonic|Notion|Supabase|Cloudflare|Highest practical value now" app/docs/connector-capability-map.md` -> pass

Blockers or caveats:
- docs-only research task; no production code changed
- connector capability availability here does not by itself mean 11Writer should adopt every service architecturally
- Supabase and Cloudflare remain high-impact surfaces that should only be used with explicit architecture and security decisions

Next recommended task:
- if the user wants a practical next step, choose one low-risk connector lane first: Linear for issue structure, Notion for planning memory, Figma for design-to-code, or LaTeX Tectonic for formal PDF exports

## 2026-05-02 12:00 America/Chicago

Task:
- notify Manager AI about the recommended macOS plugin/testing workflows and move optional native UI extras into a separate UI note

Assignment version read:
- direct user instruction; Wonder AI startup assignment `2026-05-01 15:40 America/Chicago` remains the current onboarding context

What changed:
- added a Manager-facing alert that recommends keeping the Electron-first desktop structure while selectively using the Build macOS Apps plugin for macOS-native validation and shipping workflows
- created a separate macOS-native UI extras note so launcher, menu bar, settings, and diagnostics ideas are documented without blurring the main desktop architecture
- linked the main macOS plugin workflow note to the new UI extras doc

Files touched:
- `app/docs/build-macos-apps-plugin-workflows.md`
- `app/docs/macos-native-ui-extras.md`
- `app/docs/alerts.md`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `python scripts/alerts_ledger.py` -> pass
- `rg -n "macOS Plugin Testing Guidance Added|macOS Native UI Extras|build-run-debug|packaging-notarization" app/docs` -> pass

Blockers or caveats:
- docs-only coordination task; no production code changed
- this is guidance and planning input, not proof of a working macOS-native app

Next recommended task:
- if Manager AI wants an applied next step, scope a minimal macOS runtime-control shell and validate it on a real macOS host while keeping the main workstation on the current cross-platform path

## 2026-05-02 11:34 America/Chicago

Task:
- research the `@build-macos-apps` plugin and map its workflows to 11Writer's macOS app direction

Assignment version read:
- direct user instruction; Wonder AI startup assignment `2026-05-01 15:40 America/Chicago` remains the current onboarding context

What changed:
- reviewed the local Build macOS Apps plugin skill set and its workflow contracts for run/debug, SwiftUI scene design, AppKit interop, windowing, telemetry, test triage, signing, and notarization
- checked the current 11Writer cross-platform planning docs so the recommendation aligns with the Electron-first desktop plan and shared-backend rules
- documented where the plugin is a strong fit for 11Writer, where it is a weak fit, and which workflow sequence agents should follow for native macOS work
- recorded recommended first experiments for a macOS-native launcher, runtime-control surface, or menu bar extra without implying a full native rewrite

Files touched:
- `app/docs/build-macos-apps-plugin-workflows.md`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `rg -n "Build macOS Apps Plugin Workflows For 11Writer|script/build_and_run.sh|signing-entitlements|packaging-notarization|Electron" app/docs/build-macos-apps-plugin-workflows.md` -> pass

Blockers or caveats:
- docs-only research task; no production code changed
- no macOS build or packaging run was executed from this Windows host
- the plugin is strong for native macOS surfaces and distribution work, but the repo still plans the first full desktop app around Electron plus the shared FastAPI backend

Next recommended task:
- if the user wants a practical trial, scope a minimal native macOS runtime-control shell and validate it on a real macOS host or runner before making larger architecture claims

## 2026-05-02 10:47 America/Chicago

Task:
- document Browser visual verification usage and browser-side prompt-injection / malicious-site verification guidance, and notify Manager AI

Assignment version read:
- direct user instruction; Wonder AI startup assignment `2026-05-01 15:40 America/Chicago` remains the current onboarding context

What changed:
- documented Browser Use as a rendered-page verification capability rather than a DOM-only inspection path
- added a browser-specific security verification checklist for prompt injection, phishing, malicious requests, and unsafe page behavior
- updated the existing prompt-injection defense policy to cover rendered webpage content and link the new browser guidance docs
- updated repo workflow guidance to point agents at the new browser usage and security docs
- added a low-priority Manager-facing alert for the new Browser visual verification capability and guidance

Files touched:
- `app/docs/browser-use-agent-guidelines.md`
- `app/docs/browser-use-security-verification.md`
- `app/docs/prompt-injection-defense.md`
- `app/docs/repo-workflow.md`
- `app/docs/alerts.md`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `python scripts/alerts_ledger.py` -> pass
- `rg -n "browser-use-agent-guidelines|browser-use-security-verification" app/docs` -> pass

Blockers or caveats:
- docs-only task; no production code changed
- Browser runtime recovery remains environment-dependent, but the guidance now documents how agents should use it when available

Next recommended task:
- if Manager AI adopts the guidance, broadcast the new browser verification expectations to any agent that uses Browser / Browser Use for rendered-page validation or external-site review

## 2026-05-02 09:12 America/Chicago

Task:
- verify Node.js installation and Browser plugin recovery

Assignment version read:
- direct user instruction; Wonder AI startup assignment `2026-05-01 15:40 America/Chicago` remains the current onboarding context

What changed:
- verified system Node now resolves to `v24.14.1`
- retried Browser plugin bootstrap after Node installation
- confirmed the original Node version blocker is cleared
- identified a new Browser plugin failure: `failed to start codex app-server: The system cannot find the path specified. (os error 3)`

Files touched:
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `where.exe node` -> pass
- `node --version` -> pass, `v24.14.1`
- Browser plugin bootstrap via Node REPL -> fail with Codex app-server path error, not Node version error

Blockers or caveats:
- Node.js itself is now fixed for the previous requirement
- Browser plugin still needs a separate Codex app-server/plugin environment fix

Next recommended task:
- investigate or restart/repair the Codex app Browser plugin environment before retrying browser automation

## 2026-05-01 15:48 America/Chicago

Task:
- deep dive OSINT Framework tool catalog against 11Writer guidelines

Assignment version read:
- direct user instruction; Wonder AI startup assignment `2026-05-01 15:40 America/Chicago` remains the current onboarding context

What changed:
- reviewed OSINT Framework website/GitHub structured catalog metadata
- compared tool categories and metadata against 11Writer safety, prompt-injection, source-discovery, workflow-validation, and data-source integration rules
- identified compatible candidate-source, connector, review-only, and excluded/high-risk tool classes
- generated full strict best-fit audit artifacts for 152 entries under `output/`

Files touched:
- `app/docs/agent-progress/wonder-ai.md`
- `output/osint_framework_best_fit_audit.md`
- `output/osint_framework_best_fit_audit.csv`
- `output/osint_framework_best_fit_audit.json`

Validation:
- `python` read/parse of `https://raw.githubusercontent.com/lockfale/osint-framework/master/public/arf.json` -> pass
- Browser plugin attempted; blocked by local Node REPL runtime requiring Node `>= v22.22.0` while local Node is `v22.17.1`
- generated CSV row-count sanity check -> pass, 152 checked rows

Blockers or caveats:
- no 11Writer implementation or source registry update was performed
- OSINT Framework entries are candidate leads only, not validation proof or approved source status
- correctness/truth checks are scoped to source authority, claim class, and corroboration requirements; no future source record can be treated as true solely because the directory entry exists

Next recommended task:
- if requested, create a repo-local OSINT Framework intake/routing memo or a machine-readable candidate subset for Gather/Connect review

## 2026-05-01 15:43 America/Chicago

Task:
- startup sync for Wonder AI thread

Assignment version read:
- `2026-05-01 15:40 America/Chicago`

What changed:
- read the required startup and workflow docs
- recorded that Wonder AI is user-directed
- recorded that Wonder AI is peer-level with Manager AI and Atlas AI
- recorded that Wonder AI is not a Manager-controlled domain lane
- recorded readiness for direct user instructions
- appended one startup alert to `app/docs/alerts.md`

Files touched:
- `app/docs/alerts.md`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- docs readback only

Blockers or caveats:
- none

Next recommended task:
- wait for direct user instructions

## 2026-05-04 22:55 America/Chicago

Task:
- implement the cluster-aware Source Discovery learning loop backend slice for 7Po8 complement

Assignment version read:
- direct user-provided implementation plan in chat

What changed:
- added non-network knowledge backfill and selective reclustering through `POST /api/source-discovery/jobs/knowledge-backfill`
- extended scheduler tick so it can run bounded structure scans, bounded expansion jobs, knowledge-backfill maintenance, and duplicate-aware Wave LLM task selection
- added durable Source Discovery review claim candidates plus `POST /api/source-discovery/reviews/import-claims`
- updated claim application to resolve against persisted claim candidates and populate corroborating/contradiction source lineage from knowledge-node membership
- extended memory, export, knowledge-node, and review-queue responses with pending review claim metadata
- added focused backend tests for backfill, scheduler maintenance, cluster-aware LLM selection, claim import/apply, and pending-claim review visibility
- widened the corroboration clustering heuristic just enough to group same-title, same-topic public reports that share a meaningful evidence core without treating them as near-duplicates

Files touched:
- `app/server/src/routes/source_discovery.py`
- `app/server/src/services/source_discovery_service.py`
- `app/server/src/source_discovery/db.py`
- `app/server/src/source_discovery/models.py`
- `app/server/src/types/source_discovery.py`
- `app/server/tests/test_source_discovery_memory.py`
- `app/docs/alerts.md`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `python -m pytest app/server/tests/test_source_discovery_memory.py -q` -> pass (`46 passed`)
- `python -m pytest app/server/tests/test_wave_monitor.py -q` -> pass (`25 passed`)

Blockers or caveats:
- backend-only slice; no operator UI was added
- knowledge-node clustering remains heuristic workflow infrastructure and must not be treated as truth adjudication
- scheduler maintenance remains opt-in through explicit zero-default request limits

Next recommended task:
- have Connect AI and Gather AI validate runtime-boundary and governance implications of the new cluster-aware claim and scheduler surfaces

## 2026-05-04 23:32 America/Chicago

Task:
- build the backend public-web background discovery loop that can keep finding feeds, sitemap entries, and related candidate sources over time

Assignment version read:
- direct user request in chat

What changed:
- added bounded `POST /api/source-discovery/jobs/sitemap-scan`
- added recurring public discovery cadence on source memories through `lastDiscoveryScanAt`, `nextDiscoveryScanAt`, and `discoveryScanFailCount`
- taught scheduler tick to run due public feed, sitemap, and catalog follow-up jobs through `publicDiscoveryJobLimit`
- wired the runtime scheduler worker to pass configured structure-scan, public-discovery, expansion, and knowledge-backfill limits into Source Discovery tick execution
- documented the new background public discovery behavior in the public-web workflow note

Files touched:
- `app/server/src/config/settings.py`
- `app/server/src/routes/source_discovery.py`
- `app/server/src/services/runtime_scheduler_service.py`
- `app/server/src/services/source_discovery_service.py`
- `app/server/src/source_discovery/db.py`
- `app/server/src/source_discovery/models.py`
- `app/server/src/types/source_discovery.py`
- `app/server/tests/test_source_discovery_memory.py`
- `app/docs/source-discovery-public-web-workflow.md`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `python -m compileall app/server/src` -> pass
- `python -m pytest app/server/tests/test_source_discovery_memory.py -q` -> pass (`48 passed`)
- `python -m pytest app/server/tests/test_wave_monitor.py -q` -> pass (`25 passed`)

Blockers or caveats:
- background discovery remains bounded to public no-auth surfaces and request-budgeted scheduler execution
- this still does not authorize broad crawling, login automation, CAPTCHA bypass, or automatic source approval

Next recommended task:
- if requested, add operator-facing status/inspection surfaces for due public discovery items and recent background discovery runs

## 2026-05-04 23:59 America/Chicago

Task:
- implement the next Source Discovery backend slice for seed intelligence and discovery explainability

Assignment version read:
- direct user request in chat
- reread `app/docs/spatial-intelligence-loop.md`
- reread `app/docs/fusion-layer-architecture.md`
- reread `app/docs/source-discovery-platform-plan.md`
- reread `app/docs/source-discovery-agent-framework.md`
- reread `app/docs/7po8-integration-plan.md`
- reread `app/docs/unified-user-workflows.md`

What changed:
- added root-aware Source Discovery metadata with `discoveryRole`, `seedFamily`, `sourceFamilyTags`, `scopeHints`, and `lastDiscoveryOutcome`
- added `POST /api/source-discovery/seeds/bulk` for bounded non-network root intake
- added `GET /api/source-discovery/discovery/overview`, `/discovery/queue`, and `/discovery/runs`
- changed scheduler root selection from due-time-first to discovery-priority-first for eligible structure scans and public follow-up jobs
- extended review queue, memory detail/export, and runtime status with discovery explanation fields and counts
- updated the public-web workflow doc to describe root registration, explainability surfaces, and bounded priority behavior

Files touched:
- `app/server/src/routes/source_discovery.py`
- `app/server/src/services/runtime_scheduler_service.py`
- `app/server/src/services/source_discovery_service.py`
- `app/server/src/source_discovery/db.py`
- `app/server/src/source_discovery/models.py`
- `app/server/src/types/source_discovery.py`
- `app/server/tests/test_source_discovery_memory.py`
- `app/docs/source-discovery-public-web-workflow.md`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `python -m compileall app/server/src app/server/tests/test_source_discovery_memory.py` -> pass
- `python -m pytest app/server/tests/test_source_discovery_memory.py -q` -> pass (`58 passed`)
- `python -m pytest app/server/tests/test_wave_monitor.py -q` -> pass (`25 passed`)

Blockers or caveats:
- priority is heuristic scheduler/review metadata only and must not be treated as correctness, validation, or trust
- bulk seed breadth still stays inside the current public no-auth/no-CAPTCHA rules
- external search-provider adapters and larger platform-specific discovery adapters remain future work

Next recommended task:
- add bounded public-web adapters and richer seed packets now that root observability and prioritization exist

## 2026-05-05 09:50 America/Chicago

Task:
- continue the Source Discovery backend by making long-tail public-web discovery platform-aware for harder-to-find boards and wiki-style sites

Assignment version read:
- `2026-05-01 15:40 America/Chicago`

What changed:
- added `platformFamily` to Source Discovery memory and discovery/review surfaces
- taught bounded `structure-scan` to fingerprint public Discourse and MediaWiki roots and emit derived public feed/navigation roots
- added platform-family counts to discovery overview and platform-family filtering to discovery queue
- preserved the current 11Writer boundary: platform hints are review/runtime metadata only and do not approve, trust, or auto-schedule a source outside existing bounded public rules

Files touched:
- `app/server/src/routes/source_discovery.py`
- `app/server/src/services/source_discovery_service.py`
- `app/server/src/source_discovery/db.py`
- `app/server/src/source_discovery/models.py`
- `app/server/src/types/source_discovery.py`
- `app/server/tests/test_source_discovery_memory.py`
- `app/docs/source-discovery-public-web-workflow.md`
- `app/docs/agent-progress/wonder-ai.md`
- `app/docs/alerts.md`

Validation:
- `python -m compileall app/server/src app/server/tests/test_source_discovery_memory.py` -> pass
- `python -m pytest app/server/tests/test_source_discovery_memory.py -q` -> pass (`61 passed`)
- `python -m pytest app/server/tests/test_wave_monitor.py -q` -> pass (`25 passed`)
- `python scripts/alerts_ledger.py` -> pass

Blockers or caveats:
- current platform-aware discovery is intentionally small: Discourse and MediaWiki root derivation are implemented first, while broader board/forum/status adapters still remain future bounded work
- platform family is explainability metadata and scheduler guidance only; it must not be treated as correctness, validation, or source-trust proof

Next recommended task:
- add the next bounded adapter set for public long-tail platforms, likely status-page and federated/Mastodon discovery roots, without widening into search-provider crawling

## 2026-05-05 10:15 America/Chicago

Task:
- implement the next Source Discovery backend slice for bounded Statuspage and Mastodon public-root discovery

Assignment version read:
- `2026-05-01 15:40 America/Chicago`

What changed:
- extended `structure-scan` so it now fingerprints public Statuspage and Mastodon roots and derives bounded same-origin child roots
- reused `catalog-scan` as the bounded follow-up path for public Statuspage history or component pages and public Mastodon instance, tag, account, and status pages
- tightened discovery priority and review explanations so Statuspage roots show up as official status/outage context and Mastodon roots show up as federated/public-social discovery roots
- kept the slice inside current rules: no private Statuspage support, no Mastodon search or timeline discovery, no auth or CAPTCHA handling, and no automatic approval or trust promotion

Files touched:
- `app/server/src/services/source_discovery_service.py`
- `app/server/tests/test_source_discovery_memory.py`
- `app/docs/source-discovery-public-web-workflow.md`
- `app/docs/agent-progress/wonder-ai.md`
- `app/docs/alerts.md`

Validation:
- `python -m compileall app/server/src app/server/tests/test_source_discovery_memory.py` -> pass
- `python -m pytest app/server/tests/test_source_discovery_memory.py -q` -> pass (`69 passed`)

Blockers or caveats:
- Mastodon support stays bounded to public instance metadata, visible tag/account roots, and candidate-only status URLs discovered from allowed roots
- Statuspage support stays bounded to visible public history, incident, and component/status surfaces and does not synthesize private or manage API endpoints

Next recommended task:
- add the next bounded platform adapters for public status/forum ecosystems or wait for direct user instructions

## 2026-05-05 12:34 America/Chicago

Task:
- implement the next Source Discovery backend slice for Stack Exchange queryless roots plus curated regional/local seed packets

Assignment version read:
- `2026-05-01 15:40 America/Chicago`

What changed:
- extended Source Discovery `structure-scan` and `catalog-scan` so they now fingerprint and follow bounded public Stack Exchange roots without deriving search, auth, or broad network-query behavior
- added seed-packet lineage to bulk seed intake and carried that lineage through source memories, memory export, discovery queue, and review queue surfaces
- kept the slice inside current rules: public only, no auth or CAPTCHA handling, candidate/review infrastructure only, no auto-approval, and no free-form search discovery
- the narrow shared validation blocker did not reproduce during this slice; shared backend suites collected and passed without needing a media-evidence repair

Files touched:
- `app/server/src/services/source_discovery_service.py`
- `app/server/src/source_discovery/db.py`
- `app/server/src/source_discovery/models.py`
- `app/server/src/types/source_discovery.py`
- `app/server/tests/test_source_discovery_memory.py`
- `app/docs/source-discovery-public-web-workflow.md`
- `app/docs/agent-progress/wonder-ai.md`
- `app/docs/alerts.md`

Validation:
- `python -m compileall app/server/src` -> pass
- `python -m pytest app/server/tests/test_source_discovery_memory.py -q` -> pass (`77 passed`)
- `python -m pytest app/server/tests/test_wave_monitor.py -q` -> pass (`25 passed`)
- `python -m pytest app/server/tests/test_analyst_workbench.py -q` -> pass (`5 passed`)

Blockers or caveats:
- Stack Exchange support is intentionally queryless and bounded to visible tag pages, paired tag APIs, same-site question URLs, and explicit `info` or `tags` API roots
- seed-packet provenance is explainability metadata only and must not be treated as validation or trust proof

Next recommended task:
- add the next bounded long-tail adapter family or wait for direct user instructions

Required entry shape:

```md
## 2026-05-01 15:40 America/Chicago

Task:
- short mission statement

Assignment version read:
- `2026-05-01 15:40 America/Chicago`

What changed:
- concise summary of completed work

Files touched:
- `path/to/file`

Validation:
- `command` -> pass/fail

Blockers or caveats:
- concise note

Next recommended task:
- concise next assignment or "wait for direct user instructions"
```

## 2026-05-05 20:28 America/Chicago

Task:
- implement the research-grade Source Discovery breadth slice for archive-index discovery, public mailing-list archive adapters, and curated directory or regional-portal discovery

Assignment version read:
- `2026-05-01 15:40 America/Chicago`

What changed:
- added bounded `archive-index-scan` support for public archive or open-web index inputs with candidate-only original-URL recovery for `wayback_cdx`, `archive_it_cdx`, `common_crawl_cdxj`, and fixture-backed `common_crawl_host_index`
- extended platform-aware Source Discovery so `structure-scan` and `catalog-scan` now detect and follow public mailing-list archive roots for HyperKitty, Pipermail, and Mailman-style public list trees without crossing into subscribe, post, auth, or private surfaces
- added bounded `directory-scan` so curated directories, association link pages, and regional portals can emit capped cross-domain public roots with packet lineage, scope hints, and normalized regional or local tags
- updated discovery priority and review explanations so mailing-list and curated-directory roots remain explicit long-tail review infrastructure rather than hidden trust signals
- documented the research-grade Source Discovery checklist in repo truth so future Source Discovery prompts can re-check implemented versus pending breadth slices

Files touched:
- `app/server/src/routes/source_discovery.py`
- `app/server/src/services/source_discovery_service.py`
- `app/server/src/types/source_discovery.py`
- `app/server/tests/test_source_discovery_memory.py`
- `app/docs/source-discovery-public-web-workflow.md`
- `app/docs/long-tail-information-discovery-strategy.md`
- `app/docs/agent-progress/wonder-ai.md`
- `app/docs/alerts.md`

Validation:
- `python -m compileall app/server/src` -> pass
- `python -m pytest app/server/tests/test_source_discovery_memory.py -q` -> pass (`82 passed`)
- `python -m pytest app/server/tests/test_wave_monitor.py -q` -> pass (`25 passed`)
- `python -m pytest app/server/tests/test_analyst_workbench.py -q` -> pass (`5 passed`)
- `python scripts/alerts_ledger.py` -> pass

Blockers or caveats:
- archive-index scan is intentionally bounded: it records public archive provenance and original URLs when available, but it does not fetch archived page bodies or auto-follow archive hits
- mailing-list and directory discovery remain candidate/review infrastructure only and must not be treated as source-validation proof, trust promotion, or broad crawling authority

Next recommended task:
- implement checklist item `4`: cross-language and locality-aware seed expansion, or wait for direct user instructions

## 2026-05-05 20:43 America/Chicago

Task:
- implement research-grade Source Discovery roadmap items `4-6`: locale seed expansion, trusted-root link-graph expansion, and archive-aware article extraction normalization

Assignment version read:
- `2026-05-01 15:40 America/Chicago`

What changed:
- added bounded `locale-seed-expand` with deterministic locale alias generation, locality-aware query shaping, GDELT DOC provider lift, locale basis persistence, and provider provenance on resulting source memories
- added bounded `link-graph-scan` plus optional scheduler support so reviewed public roots can emit one-hop root-like outbound discovery candidates without recursive crawling
- added persisted `archiveHits`, archive-aware `article-fetch`, archive-wrapper normalization, archive-host gating, snapshot retrieval-origin metadata, and detected-language merge-back into source memory scope hints
- updated discovery, review, memory-detail, export, and scheduler contracts so locale/provider and archive/link-graph provenance stay visible as review/runtime metadata rather than hidden trust signals

Files touched:
- `app/server/src/config/settings.py`
- `app/server/src/routes/source_discovery.py`
- `app/server/src/services/content_extraction.py`
- `app/server/src/services/runtime_scheduler_service.py`
- `app/server/src/services/source_discovery_service.py`
- `app/server/src/source_discovery/db.py`
- `app/server/src/source_discovery/models.py`
- `app/server/src/types/source_discovery.py`
- `app/server/tests/test_source_discovery_memory.py`
- `app/docs/long-tail-information-discovery-strategy.md`
- `app/docs/source-discovery-public-web-workflow.md`
- `app/docs/alerts.md`
- `app/docs/agent-progress/wonder-ai.md`

Validation:
- `python -m compileall app/server/src app/server/tests/test_source_discovery_memory.py` -> pass
- `python -m pytest app/server/tests/test_source_discovery_memory.py -q` -> pass (`88 passed`)
- `python -m pytest app/server/tests/test_wave_monitor.py -q` -> pass (`25 passed`)
- `python -m pytest app/server/tests/test_analyst_workbench.py -q` -> pass (`5 passed`)
- `python scripts/alerts_ledger.py` -> pass

Blockers or caveats:
- locale expansion remains bounded to explicit terms, explicit locale inputs, and public provider results; it is not open-ended translation or generic search scraping
- link-graph scan is one-hop and root-like only; it excludes article/post/search/share/download targets and does not recurse
- archive-body fetch requires an explicit public capture reference from an allowed archive host and does not browse archive indexes or follow archived child links

Next recommended task:
- implement checklist item `7`: event-level corroboration and contradiction graphing, or wait for direct user instructions
