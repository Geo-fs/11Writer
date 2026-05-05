# Wave LLM Interpretation Framework

Waves use LLMs for the parts deterministic code cannot do well, such as understanding article body text, extracting candidate claims, translating prose into structured review packets, and suggesting corroboration checks.

Core rule:

- LLMs propose interpretation; deterministic code babysits, validates, stores caveats, and decides what can move forward.

The current backend slice supports managed BYOK/provider configuration, per-wave provider overrides, a shared provider-adapter execution seam, explicit task creation, explicit task execution, audited execution history, validated review submission, and a bounded Source Discovery scheduler bridge that can create review-only `source_summary` or `article_claim_extraction` tasks from eligible snapshots.

Runtime-boundary rule:

- provider configuration, BYOK state, execution history, request budgets, and runtime controls are runtime-boundary and review-only surfaces
- they are not source-approval proof, claim-truth proof, or workflow-validation proof for any external source

## Supported Provider Families

The framework recognizes these provider families:

- `fixture`
- `openai`
- `anthropic`
- `xai`
- `google`
- `openrouter`
- `ollama`
- `openclaw`
- `custom`

User-owned configuration inputs:

- `WAVE_LLM_ENABLED`
- `WAVE_LLM_DEFAULT_PROVIDER`
- `WAVE_LLM_DEFAULT_MODEL`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `XAI_API_KEY`
- `GOOGLE_AI_API_KEY`
- `OPENROUTER_API_KEY`
- `OLLAMA_BASE_URL`
- `OPENCLAW_BASE_URL`
- `WAVE_LLM_MAX_INPUT_CHARS`
- `WAVE_LLM_MAX_OUTPUT_CHARS`

Runtime-managed provider settings now include:

- global defaults:
  - provider
  - model
  - allow-network default
  - request-budget default
  - retry default
  - timeout default
- per-provider settings:
  - saved API key when applicable
  - base URL when applicable
  - provider-level default model
  - provider-level network/budget/retry/timeout defaults
- per-wave settings:
  - provider override
  - model override
  - allow-network override
  - request-budget override
  - retry override
  - timeout override

API responses must only expose configured/not-configured state, config source names, and masked secret fingerprints. They must never return raw API keys.

## Current Routes

- `GET /api/tools/waves/llm/capabilities`
- `GET /api/tools/waves/llm/config`
- `POST /api/tools/waves/llm/config/defaults`
- `POST /api/tools/waves/llm/config/providers/{provider}`
- `POST /api/tools/waves/llm/config/monitors/{monitor_id}`
- `POST /api/tools/waves/llm/tasks`
- `POST /api/tools/waves/llm/tasks/{task_id}/execute`
- `POST /api/tools/waves/llm/reviews`
- `GET /api/tools/waves/llm/reviews`
- `GET /api/tools/waves/llm/executions`

Current storage:

- `wave_llm_tasks`
- `wave_llm_reviews`
- `wave_llm_executions`
- `wave_llm_monitor_preferences`
- local user-data provider config JSON

Current executable adapters:

- `fixture`: deterministic local JSON output, no network
- `ollama`: live local adapter path, blocked unless `allowNetwork=true` and `requestBudget > 0`
- `openai`: live BYOK adapter path, blocked unless `allowNetwork=true`, `requestBudget > 0`, and a configured key exists
- `openrouter`: live BYOK adapter path, blocked unless `allowNetwork=true`, `requestBudget > 0`, and a configured key exists
- `anthropic`: live BYOK adapter path, blocked unless `allowNetwork=true`, `requestBudget > 0`, and a configured key exists
- `xai`: live BYOK adapter path, blocked unless `allowNetwork=true`, `requestBudget > 0`, and a configured key exists
- `google`: live BYOK adapter path, blocked unless `allowNetwork=true`, `requestBudget > 0`, and a configured key exists
- `openclaw`: live base-URL adapter path, blocked unless `allowNetwork=true`, `requestBudget > 0`, and a configured base URL exists

Current capability-only adapter:

- `custom`

Mock execution remains supported for provider-safe contract testing. Models prefixed with `mock-` or `test-mock-` execute deterministically with no provider network call.

## Babysitting Rules

LLM output must never directly:

- promote a source
- change source reputation
- activate a connector
- create a trusted fact
- accuse people or groups
- bypass source policy
- bypass human or deterministic review

LLM output can:

- summarize article meaning
- extract candidate claims
- identify uncertainty and caveats
- suggest source checks
- suggest corroboration paths
- translate article text into structured review input

Every LLM review must preserve:

- provider
- model
- monitor id
- task type
- source ids
- record ids
- raw output
- parsed claims
- rejected claims
- risk flags
- caveats
- human-review requirement

Every LLM execution must preserve:

- task id
- provider
- model
- adapter status
- request budget
- used requests
- retry count
- timeout seconds
- raw output when present
- error summary when blocked or failed
- caveats

## Output Contract

Expected model output should be JSON:

```json
{
  "claims": [
    {
      "claimText": "The article says a consumer warning described a scam pattern.",
      "claimType": "event",
      "evidenceBasis": "source-reported",
      "confidence": 0.61
    }
  ],
  "proposedActions": ["seek-corroboration", "inspect-source"]
}
```

Allowed claim types:

- `event`
- `timing`
- `location`
- `state`
- `change`
- `attribution`
- `forecast`

Allowed evidence bases:

- `contextual`
- `source-reported`
- `derived`

The validator caps accepted claim confidence at `0.85`. This prevents weak local models from laundering certainty into the system.

The validator also filters proposed actions to the allowed set:

- `inspect-source`
- `seek-corroboration`
- `mark-unresolved`
- `move-on`

Forbidden action language such as connector activation, source promotion, or reputation changes is risk-flagged.

## Provider Adapter Rules

Provider adapters must:

- implement the shared adapter contract so every provider goes through the same request budget, timeout, retry, audit, and review path
- run only when `WAVE_LLM_ENABLED=true` or when explicitly fixture/manual
- use BYOK credentials from runtime config or user-secured storage
- avoid logging raw keys
- enforce input/output character caps
- request structured JSON output
- preserve raw output for audit
- return provider/model metadata
- handle provider failure as source/tool health, not wave truth
- never bypass the review validator
- require explicit network permission and positive request budget for live calls
- return blocked/not-implemented status instead of silently falling back to another provider

Provider adapters should return raw model output into the review path. The review path is the gate.

## Execution Rules

Task execution is explicit:

1. Create an interpretation task.
2. Resolve provider/model/defaults from runtime config, per-wave preference, and explicit request overrides.
3. Execute that task with a specific adapter, budget, timeout, and network permission.
4. Store execution output.
5. Submit output through the review validator.
6. Treat accepted claims as review candidates only.

Automated execution is allowed only through bounded scheduler controls that still create explicit tasks, preserve audit rows, respect request budgets, and keep outputs review-only.

No connector loop or arbitrary runtime shortcut should bypass the explicit task, execution, and review path.

Current bounded automation:

- Source Discovery scheduler ticks may create `source_summary` or `article_claim_extraction` tasks from eligible stored snapshots
- scheduler-created tasks must use the same adapter contract, request-budget rules, provider gating, per-wave provider preferences, and review validator as manual tasks
- provider execution remains bounded by runtime settings such as `llmTaskLimit`, `requestBudget`, and `allowNetwork`

## Local Model Posture

Cheap/free local models are allowed, but treated as low-trust assistants.

Required posture:

- assume hallucination is possible
- assume JSON may be malformed
- assume confidence scores are inflated
- require deterministic schema validation
- require human review before promotion
- require corroboration before source reputation changes

## Agent Guidance

Agents adding LLM work should:

- add provider adapters through the shared execution adapter seam behind `WaveLlmService`
- keep new provider-management fields wired through the shared runtime config service instead of reading raw settings directly
- keep model output inert until validated
- write tests for malformed JSON, unsupported claim types, overconfident claims, and accusatory language
- keep live-provider tests monkeypatched or fixture-backed unless the user explicitly requests a real provider call
- avoid direct calls from Wave Monitor run loops until scheduler/provider budget controls exist
- keep source text and LLM output separate from verified evidence
- notify Manager AI when changing shared LLM provider behavior
- prefer fixture tests first, then adapter tests with mocked provider responses
- keep new cloud provider adapters off by default until retry, timeout, budget, and cost controls are explicit

Do not build a chatbot workflow here. This is a wave interpretation layer.
