from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from sqlalchemy import select

from src.config.settings import Settings
from src.services.wave_llm_adapters import (
    WaveLlmAdapterRequest,
    execute_wave_llm_adapter,
    provider_adapter_caveat,
)
from src.services.wave_llm_provider_config_service import (
    SUPPORTED_WAVE_LLM_PROVIDERS,
    WaveLlmProviderConfigService,
)
from src.types.wave_monitor import (
    WaveLlmCapabilityResponse,
    WaveLlmConfigResponse,
    WaveLlmDefaultsUpdateRequest,
    WaveLlmExecutionHistoryItem,
    WaveLlmExecutionHistoryResponse,
    WaveLlmExecutionResponse,
    WaveLlmExecutionSummary,
    WaveLlmInterpretationTaskRequest,
    WaveLlmInterpretationTaskResponse,
    WaveLlmMonitorPreferenceUpdateRequest,
    WaveLlmProvider,
    WaveLlmProviderConfigUpdateRequest,
    WaveLlmProviderStatus,
    WaveLlmReviewQueueItem,
    WaveLlmReviewQueueResponse,
    WaveLlmReviewRequest,
    WaveLlmReviewResponse,
    WaveLlmReviewSummary,
    WaveLlmTaskExecuteRequest,
    WaveLlmTaskSummary,
    WaveLlmValidatedClaim,
)
from src.wave_monitor.db import session_scope
from src.wave_monitor.models import (
    WaveLlmExecutionORM,
    WaveLlmReviewORM,
    WaveLlmTaskORM,
    WaveMonitorORM,
)


WAVE_LLM_GUARDRAILS = [
    "LLM output is proposed interpretation only; it never directly becomes fact, source reputation, or user-visible accusation.",
    "Cheap/local models must be babysat: every claim is schema-validated, caveated, and requires review before promotion.",
    "LLMs may summarize, extract candidate claims, translate prose into structured review packets, and suggest next checks.",
    "LLMs must not activate connectors, promote sources, accuse people, bypass source rules, or change reputation scores directly.",
    "Provider keys are user-owned BYOK configuration and must not be exposed through capability responses.",
]

ALLOWED_PROPOSED_ACTIONS = {
    "inspect-source",
    "seek-corroboration",
    "mark-unresolved",
    "move-on",
}


class WaveLlmService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._provider_config = WaveLlmProviderConfigService(settings)

    def capabilities(self) -> WaveLlmCapabilityResponse:
        defaults = self._provider_config.effective_defaults()
        providers = [
            _provider_status_from_summary(self._provider_config.provider_summary(provider))
            for provider in SUPPORTED_WAVE_LLM_PROVIDERS
        ]
        return WaveLlmCapabilityResponse(
            enabled=self._settings.wave_llm_enabled,
            default_provider=defaults.default_provider,
            default_model=defaults.default_model,
            providers=providers,
            guardrails=WAVE_LLM_GUARDRAILS,
        )

    def config(self) -> WaveLlmConfigResponse:
        return self._provider_config.config_response()

    def update_defaults(self, request: WaveLlmDefaultsUpdateRequest) -> WaveLlmConfigResponse:
        return self._provider_config.update_defaults(request)

    def update_provider_config(
        self,
        provider: WaveLlmProvider,
        request: WaveLlmProviderConfigUpdateRequest,
    ) -> WaveLlmConfigResponse:
        return self._provider_config.update_provider(provider, request)

    def update_monitor_preference(
        self,
        monitor_id: str,
        request: WaveLlmMonitorPreferenceUpdateRequest,
    ) -> WaveLlmConfigResponse:
        self._provider_config.update_monitor_preference(monitor_id, request)
        return self._provider_config.config_response()

    def create_interpretation_task(
        self,
        request: WaveLlmInterpretationTaskRequest,
    ) -> WaveLlmInterpretationTaskResponse:
        now = _utc_now()
        if len(request.input_text) > self._settings.wave_llm_max_input_chars:
            raise ValueError("LLM interpretation input exceeds configured max input characters.")

        profile = self._provider_config.resolve_task_profile(
            monitor_id=request.monitor_id,
            requested_provider=request.provider,
            requested_model=request.model,
        )
        if profile.provider not in SUPPORTED_WAVE_LLM_PROVIDERS:
            raise ValueError(f"Unsupported LLM provider: {profile.provider}")

        with session_scope(self._settings.wave_monitor_database_url) as session:
            monitor = session.get(WaveMonitorORM, request.monitor_id)
            if monitor is None:
                raise ValueError(f"Unknown monitor_id: {request.monitor_id}")
            task = WaveLlmTaskORM(
                task_id=f"wave-llm-task:{_safe_id(request.monitor_id)}:{_compact_timestamp(now)}",
                monitor_id=request.monitor_id,
                task_type=request.task_type,
                provider=profile.provider,
                model=profile.model,
                status="pending_review",
                input_summary=_summarize_input(request.input_text),
                source_ids_json=json.dumps(request.source_ids),
                record_ids_json=json.dumps(request.record_ids),
                prompt_contract_json=json.dumps(_prompt_contract(request.task_type)),
                created_at=now,
                completed_at=None,
                caveats_json=json.dumps(request.caveats + [
                    "Task stores interpretation scope only; provider execution is adapter-controlled and not automatic.",
                ]),
            )
            session.add(task)
            session.flush()
            return WaveLlmInterpretationTaskResponse(
                task=_serialize_task(task),
                guardrails=WAVE_LLM_GUARDRAILS,
            )

    def submit_review(self, request: WaveLlmReviewRequest) -> WaveLlmReviewResponse:
        now = _utc_now()
        if len(request.raw_output) > self._settings.wave_llm_max_output_chars:
            raise ValueError("LLM review output exceeds configured max output characters.")

        with session_scope(self._settings.wave_monitor_database_url) as session:
            task = session.get(WaveLlmTaskORM, request.task_id)
            if task is None:
                raise ValueError(f"Unknown task_id: {request.task_id}")
            parsed = _parse_llm_output(request.raw_output)
            claims = [_validate_claim(claim) for claim in parsed["claims"]]
            accepted = [claim for claim in claims if claim.status == "accepted_for_review"]
            rejected = [claim for claim in claims if claim.status == "rejected"]
            risk_flags = _risk_flags(request.raw_output, claims)
            validation_state = "needs_human_review" if accepted else "rejected"
            provider = request.provider or task.provider
            review = WaveLlmReviewORM(
                review_id=f"wave-llm-review:{_safe_id(task.task_id)}:{_compact_timestamp(now)}",
                task_id=task.task_id,
                monitor_id=task.monitor_id,
                provider=provider,
                model=request.model or task.model,
                raw_output=request.raw_output,
                parsed_claims_json=json.dumps([claim.model_dump(mode="json") for claim in claims]),
                proposed_actions_json=json.dumps(parsed["proposed_actions"]),
                validation_state=validation_state,
                risk_flags_json=json.dumps(risk_flags),
                accepted_claim_count=len(accepted),
                rejected_claim_count=len(rejected),
                requires_human_review=True,
                created_at=now,
                caveats_json=json.dumps(request.caveats + [
                    "Accepted claims are review candidates only and require corroboration.",
                ]),
            )
            task.status = validation_state
            task.completed_at = now
            session.add(review)
            session.flush()
            return WaveLlmReviewResponse(
                task=_serialize_task(task),
                review=_serialize_review(review),
                guardrails=WAVE_LLM_GUARDRAILS,
            )

    def execute_task(self, request: WaveLlmTaskExecuteRequest) -> WaveLlmExecutionResponse:
        if request.request_budget is not None and request.request_budget < 0:
            raise ValueError("request_budget must be zero or greater.")
        now = _utc_now()
        with session_scope(self._settings.wave_monitor_database_url) as session:
            task = session.get(WaveLlmTaskORM, request.task_id)
            if task is None:
                raise ValueError(f"Unknown task_id: {request.task_id}")
            serialized_task = _serialize_task(task)
            provider = _coerce_provider(task.provider)
            options = self._provider_config.resolve_execution_options(
                monitor_id=task.monitor_id,
                provider=provider,
                allow_network=request.allow_network,
                request_budget=request.request_budget,
                max_retries=request.max_retries,
                timeout_seconds=request.timeout_seconds,
            )
            provider_config = self._provider_config.resolved_provider(provider)

        execution = _execute_adapter(
            settings=self._settings,
            task=serialized_task,
            allow_network=options.allow_network,
            request_budget=options.request_budget,
            max_retries=options.max_retries,
            timeout_seconds=options.timeout_seconds,
            api_key=provider_config.api_key,
            base_url=provider_config.base_url,
            caveats=request.caveats,
        )

        review: WaveLlmReviewSummary | None = None
        if execution.raw_output:
            review_response = self.submit_review(
                WaveLlmReviewRequest(
                    task_id=request.task_id,
                    raw_output=execution.raw_output,
                    provider=provider,
                    model=serialized_task.model,
                    caveats=execution.caveats + ["Review was created from explicit LLM task execution."],
                )
            )
            serialized_task = review_response.task
            review = review_response.review

        with session_scope(self._settings.wave_monitor_database_url) as session:
            task = session.get(WaveLlmTaskORM, request.task_id)
            if task is not None and review is None:
                if execution.status == "blocked":
                    task.status = "execution_blocked"
                elif execution.status == "failed":
                    task.status = "execution_failed"
                else:
                    task.status = "execution_completed"
                task.completed_at = now
            execution_row = WaveLlmExecutionORM(
                execution_id=f"wave-llm-exec:{_safe_id(request.task_id)}:{_compact_timestamp(now)}",
                task_id=request.task_id,
                review_id=review.review_id if review is not None else None,
                monitor_id=serialized_task.monitor_id,
                provider=serialized_task.provider,
                model=serialized_task.model,
                status=execution.status,
                adapter_status=execution.adapter_status,
                allow_network=options.allow_network,
                request_budget=execution.request_budget,
                used_requests=execution.used_requests,
                retry_count=execution.retry_count,
                timeout_seconds=options.timeout_seconds,
                raw_output=execution.raw_output,
                error_summary=execution.error_summary,
                review_validation_state=review.validation_state if review is not None else None,
                created_at=now,
                caveats_json=json.dumps(execution.caveats),
            )
            session.add(execution_row)
            session.flush()

        return WaveLlmExecutionResponse(
            task=serialized_task,
            execution=execution,
            review=review,
            guardrails=WAVE_LLM_GUARDRAILS,
        )

    def list_reviews(
        self,
        *,
        limit: int = 20,
        validation_state: str | None = None,
        requires_human_review: bool | None = None,
    ) -> WaveLlmReviewQueueResponse:
        items: list[WaveLlmReviewQueueItem] = []
        with session_scope(self._settings.wave_monitor_database_url) as session:
            stmt = select(WaveLlmReviewORM).order_by(WaveLlmReviewORM.created_at.desc()).limit(max(1, limit))
            if validation_state:
                stmt = stmt.where(WaveLlmReviewORM.validation_state == validation_state)
            if requires_human_review is not None:
                stmt = stmt.where(WaveLlmReviewORM.requires_human_review == requires_human_review)
            reviews = list(session.scalars(stmt))
            task_ids = [review.task_id for review in reviews]
            tasks = {
                task.task_id: task
                for task in session.scalars(select(WaveLlmTaskORM).where(WaveLlmTaskORM.task_id.in_(task_ids)))
            } if task_ids else {}
            for review in reviews:
                task = tasks.get(review.task_id)
                if task is None:
                    continue
                source_ids = _loads_list(task.source_ids_json)
                record_ids = _loads_list(task.record_ids_json)
                items.append(
                    WaveLlmReviewQueueItem(
                        task=_serialize_task(task),
                        review=_serialize_review(review),
                        source_ids=source_ids,
                        record_ids=record_ids,
                        primary_source_id=source_ids[0] if len(source_ids) == 1 else None,
                    )
                )
        return WaveLlmReviewQueueResponse(
            metadata={
                "count": len(items),
                "validationState": validation_state or "all",
                "requiresHumanReview": requires_human_review,
            },
            items=items,
            guardrails=WAVE_LLM_GUARDRAILS,
        )

    def list_executions(
        self,
        *,
        limit: int = 20,
        monitor_id: str | None = None,
    ) -> WaveLlmExecutionHistoryResponse:
        items: list[WaveLlmExecutionHistoryItem] = []
        with session_scope(self._settings.wave_monitor_database_url) as session:
            stmt = select(WaveLlmExecutionORM).order_by(WaveLlmExecutionORM.created_at.desc()).limit(max(1, limit))
            if monitor_id:
                stmt = stmt.where(WaveLlmExecutionORM.monitor_id == monitor_id)
            executions = list(session.scalars(stmt))
            task_ids = [execution.task_id for execution in executions]
            tasks = {
                task.task_id: task
                for task in session.scalars(select(WaveLlmTaskORM).where(WaveLlmTaskORM.task_id.in_(task_ids)))
            } if task_ids else {}
            for execution in executions:
                task = tasks.get(execution.task_id)
                if task is None:
                    continue
                items.append(_serialize_execution_history_item(execution, task))
        return WaveLlmExecutionHistoryResponse(
            metadata={
                "count": len(items),
                "monitorId": monitor_id,
            },
            items=items,
            guardrails=WAVE_LLM_GUARDRAILS,
        )


def _provider_status_from_summary(summary) -> WaveLlmProviderStatus:
    caveats = list(summary.caveats)
    adapter_caveat = provider_adapter_caveat(summary.provider)
    if adapter_caveat and adapter_caveat not in caveats:
        caveats.append(adapter_caveat)
    return WaveLlmProviderStatus(
        provider=summary.provider,
        configured=summary.configured,
        key_source=summary.key_source,
        local=summary.local,
        caveats=caveats,
    )


def _execute_adapter(
    *,
    settings: Settings,
    task: WaveLlmTaskSummary,
    allow_network: bool,
    request_budget: int,
    max_retries: int,
    timeout_seconds: int,
    api_key: str | None,
    base_url: str | None,
    caveats: list[str],
) -> WaveLlmExecutionSummary:
    return execute_wave_llm_adapter(
        WaveLlmAdapterRequest(
            settings=settings,
            task=task,
            allow_network=allow_network,
            request_budget=request_budget,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            api_key=api_key,
            base_url=base_url,
            caveats=caveats,
        )
    )


def _prompt_contract(task_type: str) -> dict[str, object]:
    return {
        "taskType": task_type,
        "requiredOutput": {
            "claims": [
                {
                    "claimText": "string",
                    "claimType": "event|timing|location|state|change|attribution|forecast",
                    "evidenceBasis": "contextual|source-reported|derived",
                    "confidence": "0.0-1.0",
                }
            ],
            "proposedActions": ["inspect-source|seek-corroboration|mark-unresolved|move-on"],
        },
        "forbidden": [
            "direct source promotion",
            "reputation score changes",
            "accusations or culpability claims",
            "connector activation",
        ],
    }


def _parse_llm_output(raw_output: str) -> dict[str, object]:
    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        return {"claims": [], "proposed_actions": []}
    claims = parsed.get("claims", [])
    proposed_actions = parsed.get("proposedActions", parsed.get("proposed_actions", []))
    actions = [
        str(action)
        for action in proposed_actions
        if isinstance(action, str) and action in ALLOWED_PROPOSED_ACTIONS
    ] if isinstance(proposed_actions, list) else []
    return {
        "claims": claims if isinstance(claims, list) else [],
        "proposed_actions": actions,
    }


def _validate_claim(raw: object) -> WaveLlmValidatedClaim:
    if not isinstance(raw, dict):
        return _rejected_claim("Malformed claim object.")
    claim_text = str(raw.get("claimText") or raw.get("claim_text") or "").strip()
    claim_type = str(raw.get("claimType") or raw.get("claim_type") or "state").strip()
    evidence_basis = str(raw.get("evidenceBasis") or raw.get("evidence_basis") or "contextual").strip()
    confidence = _safe_float(raw.get("confidence"), default=0.0)
    if len(claim_text) < 12:
        return _rejected_claim("Claim text is too short to review.", claim_text=claim_text)
    if claim_type not in {"event", "timing", "location", "state", "change", "attribution", "forecast"}:
        return _rejected_claim("Unsupported claim type.", claim_text=claim_text)
    if evidence_basis not in {"contextual", "source-reported", "derived"}:
        return _rejected_claim("Unsupported evidence basis.", claim_text=claim_text, claim_type=claim_type)
    if confidence > 0.85:
        confidence = 0.85
    return WaveLlmValidatedClaim(
        claim_text=claim_text[:1000],
        claim_type=claim_type,
        evidence_basis=evidence_basis,
        confidence=round(max(0.0, min(0.85, confidence)), 4),
        status="accepted_for_review",
        rejection_reason=None,
    )


def _rejected_claim(
    reason: str,
    *,
    claim_text: str = "",
    claim_type: str = "state",
) -> WaveLlmValidatedClaim:
    return WaveLlmValidatedClaim(
        claim_text=claim_text[:1000],
        claim_type=claim_type,
        evidence_basis="contextual",
        confidence=0.0,
        status="rejected",
        rejection_reason=reason,
    )


def _risk_flags(raw_output: str, claims: list[WaveLlmValidatedClaim]) -> list[str]:
    lowered = raw_output.casefold()
    flags = []
    if not claims:
        flags.append("no_valid_claims")
    if any(term in lowered for term in ("guilty", "culprit", "criminal", "terrorist", "murderer")):
        flags.append("accusatory_language")
    if any(claim.confidence >= 0.85 for claim in claims):
        flags.append("confidence_ceiling_applied")
    if any(claim.status == "rejected" for claim in claims):
        flags.append("some_claims_rejected")
    if any(term in lowered for term in ("ignore previous", "system prompt", "developer message", "bypass guardrails")):
        flags.append("prompt_injection_language")
    if any(term in lowered for term in ("activate connector", "change reputation", "promote source", "mark verified")):
        flags.append("forbidden_action_language")
    return flags


def _serialize_task(task: WaveLlmTaskORM) -> WaveLlmTaskSummary:
    return WaveLlmTaskSummary(
        task_id=task.task_id,
        monitor_id=task.monitor_id,
        task_type=task.task_type,
        provider=task.provider,
        model=task.model,
        status=task.status,
        input_summary=task.input_summary,
        source_ids=_loads_list(task.source_ids_json),
        record_ids=_loads_list(task.record_ids_json),
        created_at=task.created_at,
        completed_at=task.completed_at,
        caveats=_loads_list(task.caveats_json),
    )


def _serialize_review(review: WaveLlmReviewORM) -> WaveLlmReviewSummary:
    return WaveLlmReviewSummary(
        review_id=review.review_id,
        task_id=review.task_id,
        monitor_id=review.monitor_id,
        provider=review.provider,
        model=review.model,
        validation_state=review.validation_state,
        claims=[WaveLlmValidatedClaim(**claim) for claim in _loads_json_list(review.parsed_claims_json)],
        proposed_actions=_loads_list(review.proposed_actions_json),
        risk_flags=_loads_list(review.risk_flags_json),
        accepted_claim_count=review.accepted_claim_count,
        rejected_claim_count=review.rejected_claim_count,
        requires_human_review=review.requires_human_review,
        created_at=review.created_at,
        caveats=_loads_list(review.caveats_json),
    )


def _serialize_execution_history_item(
    execution: WaveLlmExecutionORM,
    task: WaveLlmTaskORM,
) -> WaveLlmExecutionHistoryItem:
    return WaveLlmExecutionHistoryItem(
        execution_id=execution.execution_id,
        task_id=execution.task_id,
        monitor_id=execution.monitor_id,
        task_type=task.task_type,
        provider=execution.provider,
        model=execution.model,
        status=execution.status,
        adapter_status=execution.adapter_status,
        allow_network=execution.allow_network,
        request_budget=execution.request_budget,
        used_requests=execution.used_requests,
        retry_count=execution.retry_count,
        timeout_seconds=execution.timeout_seconds,
        created_at=execution.created_at,
        review_id=execution.review_id,
        review_validation_state=execution.review_validation_state,
        error_summary=execution.error_summary,
        input_summary=task.input_summary,
        caveats=_loads_list(execution.caveats_json),
    )


def _summarize_input(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()[:500]


def _safe_float(value: object, *, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _loads_json_list(raw: str | None) -> list[dict[str, object]]:
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def _loads_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _compact_timestamp(value: str) -> str:
    return re.sub(r"[^0-9]", "", value)[:20]


def _safe_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower() or "unknown"


def _coerce_provider(provider: str) -> WaveLlmProvider:
    candidate = provider.strip()
    if candidate not in SUPPORTED_WAVE_LLM_PROVIDERS:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    return candidate  # type: ignore[return-value]
