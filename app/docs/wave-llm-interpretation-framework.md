# Wave LLM Interpretation Framework

Waves can use LLMs for the parts deterministic code cannot do well, such as understanding article body text, extracting candidate claims, translating prose into structured review packets, and suggesting corroboration checks.

Core rule:

- LLMs propose interpretation; deterministic code babysits, validates, stores caveats, and decides what can move forward.

The current backend slice supports BYOK/provider capability reporting, a shared provider-adapter execution seam, LLM interpretation task records, explicit task execution, validated review submission, live-gated OpenAI execution, and a bounded Source Discovery scheduler bridge that can create review-only `source_summary` or `article_claim_extraction` tasks from eligible snapshots.

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

User-owned configuration keys:

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

Capability responses must only expose configured/not-configured state and config source names. They must never return raw API keys.

## Current Routes

- `GET /api/tools/waves/llm/capabilities`
- `POST /api/tools/waves/llm/tasks`
- `POST /api/tools/waves/llm/tasks/{task_id}/execute`
- `POST /api/tools/waves/llm/reviews`

Current storage:

- `wave_llm_tasks`
- `wave_llm_reviews`

Current executable adapters:

- `fixture`: deterministic local JSON output, no network
- `ollama`: live local adapter path, blocked unless `allowNetwork=true` and `requestBudget > 0`
- `openai`: live BYOK adapter path, blocked unless `allowNetwork=true`, `requestBudget > 0`, and `OPENAI_API_KEY` is configured
- `openrouter`: deterministic mock adapter path for BYOK contract testing only; live network calls remain disabled

Current capability-only adapters:

- `anthropic`
- `xai`
- `google`
- `openclaw`
- `custom`

Capability-only means keys/configuration can be detected, but execution is blocked until a provider adapter is implemented, tested, and budget-gated.

Mock-only means the provider name can execute through the shared adapter contract, but only against deterministic local responses. It does not contact the provider network and does not prove live-provider readiness.

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

Future provider adapters must:

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
2. Execute that task with a specific adapter, budget, and network permission.
3. Store execution output.
4. Submit output through the review validator.
5. Treat accepted claims as review candidates only.

Automated execution is allowed only through bounded scheduler controls that still create explicit tasks, preserve audit rows, respect request budgets, and keep outputs review-only.

No connector loop or arbitrary runtime shortcut should bypass the explicit task, execution, and review path.

Current bounded automation:

- Source Discovery scheduler ticks may create `source_summary` or `article_claim_extraction` tasks from eligible stored snapshots
- scheduler-created tasks must use the same adapter contract, request-budget rules, provider gating, and review validator as manual tasks
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
- keep model output inert until validated
- write tests for malformed JSON, unsupported claim types, overconfident claims, and accusatory language
- keep live-provider tests monkeypatched or fixture-backed unless the user explicitly requests a real provider call
- avoid direct calls from Wave Monitor run loops until scheduler/provider budget controls exist
- keep source text and LLM output separate from verified evidence
- notify Manager AI when changing shared LLM provider behavior
- prefer fixture tests first, then adapter tests with mocked provider responses
- keep new cloud provider adapters off by default until retry, timeout, budget, and cost controls are explicit

Do not build a chatbot workflow here. This is a wave interpretation layer.
