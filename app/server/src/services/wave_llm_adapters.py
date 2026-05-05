from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from src.config.settings import Settings
from src.types.wave_monitor import WaveLlmExecutionSummary, WaveLlmTaskSummary


LIVE_PROVIDER_CAVEAT = (
    "Live execution is available only with explicit network permission, positive request budget, "
    "bounded retries, and review gating."
)


@dataclass(frozen=True)
class WaveLlmAdapterRequest:
    settings: Settings
    task: WaveLlmTaskSummary
    allow_network: bool
    request_budget: int
    max_retries: int
    timeout_seconds: int
    api_key: str | None
    base_url: str | None
    caveats: list[str]


def execute_wave_llm_adapter(request: WaveLlmAdapterRequest) -> WaveLlmExecutionSummary:
    adapter = _ADAPTERS.get(request.task.provider)
    if adapter is None:
        return _blocked_execution(
            request.task,
            request.request_budget,
            f"Provider adapter is not implemented for {request.task.provider}.",
            adapter_status="not_implemented",
            caveats=request.caveats + [
                "BYOK capability is detected, but this provider cannot execute until an adapter is implemented and tested.",
            ],
        )
    return adapter(request)


def provider_adapter_caveat(provider: str) -> str | None:
    if provider in {"openai", "openrouter", "anthropic", "xai", "google", "openclaw"}:
        return LIVE_PROVIDER_CAVEAT
    if provider == "ollama":
        return "Local Ollama execution is available only with explicit network permission, positive request budget, and review gating."
    if provider == "custom":
        return "Generic custom execution still requires a concrete endpoint contract and configuration."
    return None


def _execute_fixture(request: WaveLlmAdapterRequest) -> WaveLlmExecutionSummary:
    raw_output = _fixture_output(request.task)
    return WaveLlmExecutionSummary(
        task_id=request.task.task_id,
        provider=request.task.provider,
        model=request.task.model,
        status="completed",
        adapter_status="fixture",
        request_budget=max(0, request.request_budget),
        used_requests=0,
        retry_count=0,
        raw_output=raw_output,
        error_summary=None,
        caveats=request.caveats + [
            "Fixture adapter generated deterministic review JSON without network access.",
        ],
    )


def _execute_openai(request: WaveLlmAdapterRequest) -> WaveLlmExecutionSummary:
    return _execute_live_provider(
        request,
        provider_name="openai",
        configured=bool(request.api_key),
        missing_error="OpenAI is not configured with an API key.",
        adapter_status="openai_live",
        performer=lambda adapter_request: _perform_openai_compatible_request(
            adapter_request,
            url=(adapter_request.base_url or "https://api.openai.com/v1/chat/completions"),
            api_key=adapter_request.api_key,
        ),
        success_caveat="OpenAI output is still low-trust until review validation accepts specific claims for review.",
    )


def _execute_openrouter(request: WaveLlmAdapterRequest) -> WaveLlmExecutionSummary:
    return _execute_live_provider(
        request,
        provider_name="openrouter",
        configured=bool(request.api_key),
        missing_error="OpenRouter is not configured with an API key.",
        adapter_status="openrouter_live",
        performer=lambda adapter_request: _perform_openai_compatible_request(
            adapter_request,
            url=(adapter_request.base_url or "https://openrouter.ai/api/v1/chat/completions"),
            api_key=adapter_request.api_key,
            extra_headers={
                "HTTP-Referer": "https://local.11writer.invalid",
                "X-Title": "11Writer Wave Monitor",
            },
        ),
        success_caveat="OpenRouter output is still low-trust until review validation accepts specific claims for review.",
    )


def _execute_xai(request: WaveLlmAdapterRequest) -> WaveLlmExecutionSummary:
    return _execute_live_provider(
        request,
        provider_name="xai",
        configured=bool(request.api_key),
        missing_error="xAI is not configured with an API key.",
        adapter_status="xai_live",
        performer=lambda adapter_request: _perform_openai_compatible_request(
            adapter_request,
            url=(adapter_request.base_url or "https://api.x.ai/v1/chat/completions"),
            api_key=adapter_request.api_key,
        ),
        success_caveat="xAI output is still low-trust until review validation accepts specific claims for review.",
    )


def _execute_anthropic(request: WaveLlmAdapterRequest) -> WaveLlmExecutionSummary:
    return _execute_live_provider(
        request,
        provider_name="anthropic",
        configured=bool(request.api_key),
        missing_error="Anthropic is not configured with an API key.",
        adapter_status="anthropic_live",
        performer=_perform_anthropic_request,
        success_caveat="Anthropic output is still low-trust until review validation accepts specific claims for review.",
    )


def _execute_google(request: WaveLlmAdapterRequest) -> WaveLlmExecutionSummary:
    return _execute_live_provider(
        request,
        provider_name="google",
        configured=bool(request.api_key),
        missing_error="Google is not configured with an API key.",
        adapter_status="google_live",
        performer=_perform_google_request,
        success_caveat="Google output is still low-trust until review validation accepts specific claims for review.",
    )


def _execute_openclaw(request: WaveLlmAdapterRequest) -> WaveLlmExecutionSummary:
    return _execute_live_provider(
        request,
        provider_name="openclaw",
        configured=bool(request.base_url),
        missing_error="OpenClaw is not configured with a base URL.",
        adapter_status="openclaw_live",
        performer=lambda adapter_request: _perform_openai_compatible_request(
            adapter_request,
            url=(adapter_request.base_url or "").rstrip("/") + "/v1/chat/completions",
            api_key=adapter_request.api_key,
        ),
        success_caveat="OpenClaw output is still low-trust until review validation accepts specific claims for review.",
    )


def _execute_ollama(request: WaveLlmAdapterRequest) -> WaveLlmExecutionSummary:
    settings = request.settings
    if not settings.wave_llm_enabled:
        return _blocked_execution(request.task, request.request_budget, "Wave LLM execution is disabled by WAVE_LLM_ENABLED.")
    if not request.base_url:
        return _blocked_execution(
            request.task,
            request.request_budget,
            "Ollama is not configured with a base URL.",
            caveats=request.caveats,
        )
    if _is_mock_model(request.task.model):
        return _mock_cloud_execution("ollama", request, adapter_status="mock_ollama")
    if not request.allow_network or request.request_budget <= 0:
        return _blocked_execution(
            request.task,
            request.request_budget,
            "Ollama execution requires allow_network=true and request_budget > 0.",
            caveats=request.caveats + ["No local model request was made."],
        )
    return _execute_attempts(
        request,
        adapter_status="ollama_local",
        performer=_perform_ollama_request,
        success_caveat="Ollama local output is low-trust and must pass review validation.",
    )


def _execute_live_provider(
    request: WaveLlmAdapterRequest,
    *,
    provider_name: str,
    configured: bool,
    missing_error: str,
    adapter_status: str,
    performer,
    success_caveat: str,
) -> WaveLlmExecutionSummary:
    settings = request.settings
    if not settings.wave_llm_enabled:
        return _blocked_execution(request.task, request.request_budget, "Wave LLM execution is disabled by WAVE_LLM_ENABLED.")
    if not configured:
        return _blocked_execution(
            request.task,
            request.request_budget,
            missing_error,
            caveats=request.caveats,
        )
    if _is_mock_model(request.task.model):
        return _mock_cloud_execution(provider_name, request)
    if not request.allow_network or request.request_budget <= 0:
        return _blocked_execution(
            request.task,
            request.request_budget,
            f"{provider_name} execution requires allow_network=true and request_budget > 0.",
            caveats=request.caveats + ["No provider request was made."],
        )
    return _execute_attempts(
        request,
        adapter_status=adapter_status,
        performer=performer,
        success_caveat=success_caveat,
    )


def _execute_attempts(
    request: WaveLlmAdapterRequest,
    *,
    adapter_status: str,
    performer,
    success_caveat: str,
) -> WaveLlmExecutionSummary:
    attempts = max(1, min(3, request.max_retries + 1))
    used_requests = 0
    last_error: str | None = None
    for attempt in range(attempts):
        if used_requests >= request.request_budget:
            break
        used_requests += 1
        try:
            output = performer(request)
            if len(output) > request.settings.wave_llm_max_output_chars:
                output = output[: request.settings.wave_llm_max_output_chars]
            return WaveLlmExecutionSummary(
                task_id=request.task.task_id,
                provider=request.task.provider,
                model=request.task.model,
                status="completed" if output else "failed",
                adapter_status=adapter_status,
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                retry_count=attempt,
                raw_output=output,
                error_summary=None if output else f"{request.task.provider} returned an empty response.",
                caveats=request.caveats + [success_caveat],
            )
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
            last_error = str(exc)[:500]
            continue
    return WaveLlmExecutionSummary(
        task_id=request.task.task_id,
        provider=request.task.provider,
        model=request.task.model,
        status="failed",
        adapter_status=adapter_status,
        request_budget=max(0, request.request_budget),
        used_requests=used_requests,
        retry_count=max(0, used_requests - 1),
        raw_output="",
        error_summary=last_error or f"{request.task.provider} execution failed or exhausted request budget.",
        caveats=request.caveats + [
            "Provider failure is tool-health context, not evidence about the wave.",
        ],
    )


def _perform_openai_compatible_request(
    request: WaveLlmAdapterRequest,
    *,
    url: str,
    api_key: str | None,
    extra_headers: dict[str, str] | None = None,
) -> str:
    payload = json.dumps({
        "model": request.task.model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Return JSON only. Never accuse people, never promote sources, "
                    "never change reputation, and never suggest direct actions outside the allowed schema."
                ),
            },
            {"role": "user", "content": _adapter_prompt(request.task)},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0,
    }).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "11Writer-WaveLLM/phase2",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if extra_headers:
        headers.update(extra_headers)
    provider_request = Request(url, data=payload, headers=headers, method="POST")
    with urlopen(provider_request, timeout=request.timeout_seconds) as response:
        raw = response.read(request.settings.wave_llm_max_output_chars + 4096).decode("utf-8", errors="replace")
    parsed = json.loads(raw)
    choices = parsed.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("Provider response did not contain choices.")
    message = choices[0].get("message", {})
    content = message.get("content", "")
    if isinstance(content, list):
        text_parts = [str(item.get("text", "")) for item in content if isinstance(item, dict)]
        return "".join(text_parts).strip()
    return str(content).strip()


def _perform_anthropic_request(request: WaveLlmAdapterRequest) -> str:
    payload = json.dumps({
        "model": request.task.model,
        "max_tokens": 700,
        "temperature": 0,
        "system": (
            "Return JSON only. Never accuse people, never promote sources, "
            "never change reputation, and never suggest direct actions outside the allowed schema."
        ),
        "messages": [{"role": "user", "content": _adapter_prompt(request.task)}],
    }).encode("utf-8")
    provider_request = Request(
        (request.base_url or "https://api.anthropic.com/v1/messages"),
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "11Writer-WaveLLM/phase2",
            "x-api-key": str(request.api_key),
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urlopen(provider_request, timeout=request.timeout_seconds) as response:
        raw = response.read(request.settings.wave_llm_max_output_chars + 4096).decode("utf-8", errors="replace")
    parsed = json.loads(raw)
    content = parsed.get("content")
    if not isinstance(content, list) or not content:
        raise ValueError("Anthropic response did not contain content.")
    text_parts = [str(item.get("text", "")) for item in content if isinstance(item, dict)]
    return "".join(text_parts).strip()


def _perform_google_request(request: WaveLlmAdapterRequest) -> str:
    model = quote(request.task.model, safe="")
    url = (
        f"{(request.base_url or 'https://generativelanguage.googleapis.com/v1beta/models').rstrip('/')}/"
        f"{model}:generateContent?key={request.api_key}"
    )
    payload = json.dumps({
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "Return JSON only. Never accuse people, never promote sources, "
                            "never change reputation, and never suggest direct actions outside the allowed schema.\n\n"
                            + _adapter_prompt(request.task)
                        )
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "responseMimeType": "application/json",
        },
    }).encode("utf-8")
    provider_request = Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "11Writer-WaveLLM/phase2",
        },
        method="POST",
    )
    with urlopen(provider_request, timeout=request.timeout_seconds) as response:
        raw = response.read(request.settings.wave_llm_max_output_chars + 4096).decode("utf-8", errors="replace")
    parsed = json.loads(raw)
    candidates = parsed.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("Google response did not contain candidates.")
    content = candidates[0].get("content", {})
    parts = content.get("parts", [])
    if not isinstance(parts, list):
        raise ValueError("Google response parts were missing.")
    return "".join(str(item.get("text", "")) for item in parts if isinstance(item, dict)).strip()


def _perform_ollama_request(request: WaveLlmAdapterRequest) -> str:
    payload = json.dumps({
        "model": request.task.model,
        "prompt": _adapter_prompt(request.task),
        "stream": False,
        "format": "json",
    }).encode("utf-8")
    provider_request = Request(
        request.base_url.rstrip("/") + "/api/generate",  # type: ignore[union-attr]
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "11Writer-WaveLLM/phase2"},
        method="POST",
    )
    with urlopen(provider_request, timeout=request.timeout_seconds) as response:
        raw = response.read(request.settings.wave_llm_max_output_chars + 2048).decode("utf-8", errors="replace")
    parsed = json.loads(raw)
    return str(parsed.get("response", "")).strip()


def _blocked_execution(
    task: WaveLlmTaskSummary,
    request_budget: int,
    error_summary: str,
    *,
    adapter_status: str = "blocked",
    caveats: list[str] | None = None,
) -> WaveLlmExecutionSummary:
    return WaveLlmExecutionSummary(
        task_id=task.task_id,
        provider=task.provider,
        model=task.model,
        status="blocked",
        adapter_status=adapter_status,
        request_budget=max(0, request_budget),
        used_requests=0,
        retry_count=0,
        raw_output="",
        error_summary=error_summary,
        caveats=caveats or [],
    )


def _fixture_output(task: WaveLlmTaskSummary) -> str:
    claim_text = f"The reviewed text may contain a source-reported claim relevant to {task.monitor_id}."
    if task.input_summary:
        claim_text = f"The reviewed text says: {task.input_summary[:220]}"
    return json.dumps({
        "claims": [
            {
                "claimText": claim_text,
                "claimType": "state",
                "evidenceBasis": "source-reported",
                "confidence": 0.45,
            }
        ],
        "proposedActions": ["inspect-source", "seek-corroboration"],
    })


def _mock_cloud_output(provider_name: str, task: WaveLlmTaskSummary) -> str:
    claim_text = (
        f"Mock {provider_name} adapter interpreted the reviewed text for {task.monitor_id}: {task.input_summary[:180]}"
    )
    return json.dumps({
        "claims": [
            {
                "claimText": claim_text.strip(),
                "claimType": "state",
                "evidenceBasis": "source-reported",
                "confidence": 0.58,
            }
        ],
        "proposedActions": ["inspect-source", "seek-corroboration"],
    })


def _mock_cloud_execution(
    provider_name: str,
    request: WaveLlmAdapterRequest,
    *,
    adapter_status: str | None = None,
) -> WaveLlmExecutionSummary:
    return WaveLlmExecutionSummary(
        task_id=request.task.task_id,
        provider=request.task.provider,
        model=request.task.model,
        status="completed",
        adapter_status=adapter_status or f"mock_{provider_name}",
        request_budget=max(0, request.request_budget),
        used_requests=0,
        retry_count=0,
        raw_output=_mock_cloud_output(provider_name, request.task),
        error_summary=None,
        caveats=request.caveats + [
            f"{provider_name} execution used a deterministic mock adapter; no external provider call was made.",
        ],
    )


def _adapter_prompt(task: WaveLlmTaskSummary) -> str:
    return (
        "You are extracting candidate claims for 11Writer Wave Monitor. "
        "Return only JSON with keys claims and proposedActions. "
        "Claims must have claimText, claimType, evidenceBasis, confidence. "
        "Do not accuse people, promote sources, activate connectors, or change reputation. "
        f"Task type: {task.task_type}. Monitor: {task.monitor_id}. Text: {task.input_summary}"
    )


def _is_mock_model(model: str) -> bool:
    lowered = model.strip().casefold()
    return lowered.startswith("mock-") or lowered.startswith("test-mock-")


_ADAPTERS = {
    "fixture": _execute_fixture,
    "openai": _execute_openai,
    "openrouter": _execute_openrouter,
    "anthropic": _execute_anthropic,
    "xai": _execute_xai,
    "google": _execute_google,
    "openclaw": _execute_openclaw,
    "ollama": _execute_ollama,
}
