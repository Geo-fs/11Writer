from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from src.config.settings import Settings
from src.services.runtime_paths import resolve_runtime_paths
from src.types.wave_monitor import (
    WaveLlmConfigResponse,
    WaveLlmDefaultsSummary,
    WaveLlmDefaultsUpdateRequest,
    WaveLlmMonitorPreferenceSummary,
    WaveLlmMonitorPreferenceUpdateRequest,
    WaveLlmProvider,
    WaveLlmProviderConfigSummary,
    WaveLlmProviderConfigUpdateRequest,
)
from src.wave_monitor.db import session_scope
from src.wave_monitor.models import WaveLlmMonitorPreferenceORM, WaveMonitorORM


SUPPORTED_WAVE_LLM_PROVIDERS: list[WaveLlmProvider] = [
    "fixture",
    "openai",
    "anthropic",
    "xai",
    "google",
    "openrouter",
    "ollama",
    "openclaw",
    "custom",
]

WAVE_LLM_CONFIG_STORAGE_CAVEAT = (
    "Saved provider secrets are kept in the local user-data config file, masked in API responses, "
    "and never exposed back to the UI; OS keychain integration is still future work."
)


@dataclass(frozen=True)
class ProviderMetadata:
    provider: WaveLlmProvider
    local: bool
    adapter_mode: str
    supports_api_key: bool
    supports_base_url: bool
    default_base_url: str | None
    env_api_key_name: str | None = None
    env_base_url_name: str | None = None
    settings_api_key_attr: str | None = None
    settings_base_url_attr: str | None = None


@dataclass(frozen=True)
class ResolvedWaveLlmProviderConfig:
    provider: WaveLlmProvider
    configured: bool
    key_source: str
    local: bool
    adapter_mode: str
    supports_api_key: bool
    supports_base_url: bool
    env_fallback_configured: bool
    masked_secret: str | None
    api_key: str | None
    base_url: str | None
    default_model: str | None
    allow_network_default: bool | None
    request_budget_default: int | None
    max_retries_default: int | None
    timeout_seconds_default: int | None
    caveats: list[str]


@dataclass(frozen=True)
class ResolvedWaveLlmTaskProfile:
    provider: WaveLlmProvider
    model: str


@dataclass(frozen=True)
class ResolvedWaveLlmExecutionOptions:
    allow_network: bool
    request_budget: int
    max_retries: int
    timeout_seconds: int


PROVIDER_METADATA: dict[WaveLlmProvider, ProviderMetadata] = {
    "fixture": ProviderMetadata(
        provider="fixture",
        local=True,
        adapter_mode="fixture",
        supports_api_key=False,
        supports_base_url=False,
        default_base_url=None,
    ),
    "openai": ProviderMetadata(
        provider="openai",
        local=False,
        adapter_mode="live",
        supports_api_key=True,
        supports_base_url=True,
        default_base_url="https://api.openai.com/v1/chat/completions",
        env_api_key_name="OPENAI_API_KEY",
        settings_api_key_attr="openai_api_key",
    ),
    "anthropic": ProviderMetadata(
        provider="anthropic",
        local=False,
        adapter_mode="live",
        supports_api_key=True,
        supports_base_url=True,
        default_base_url="https://api.anthropic.com/v1/messages",
        env_api_key_name="ANTHROPIC_API_KEY",
        settings_api_key_attr="anthropic_api_key",
    ),
    "xai": ProviderMetadata(
        provider="xai",
        local=False,
        adapter_mode="live",
        supports_api_key=True,
        supports_base_url=True,
        default_base_url="https://api.x.ai/v1/chat/completions",
        env_api_key_name="XAI_API_KEY",
        settings_api_key_attr="xai_api_key",
    ),
    "google": ProviderMetadata(
        provider="google",
        local=False,
        adapter_mode="live",
        supports_api_key=True,
        supports_base_url=True,
        default_base_url="https://generativelanguage.googleapis.com/v1beta/models",
        env_api_key_name="GOOGLE_AI_API_KEY",
        settings_api_key_attr="google_ai_api_key",
    ),
    "openrouter": ProviderMetadata(
        provider="openrouter",
        local=False,
        adapter_mode="live",
        supports_api_key=True,
        supports_base_url=True,
        default_base_url="https://openrouter.ai/api/v1/chat/completions",
        env_api_key_name="OPENROUTER_API_KEY",
        settings_api_key_attr="openrouter_api_key",
    ),
    "ollama": ProviderMetadata(
        provider="ollama",
        local=True,
        adapter_mode="live",
        supports_api_key=False,
        supports_base_url=True,
        default_base_url="http://localhost:11434",
        env_base_url_name="OLLAMA_BASE_URL",
        settings_base_url_attr="ollama_base_url",
    ),
    "openclaw": ProviderMetadata(
        provider="openclaw",
        local=True,
        adapter_mode="live",
        supports_api_key=False,
        supports_base_url=True,
        default_base_url=None,
        env_base_url_name="OPENCLAW_BASE_URL",
        settings_base_url_attr="openclaw_base_url",
    ),
    "custom": ProviderMetadata(
        provider="custom",
        local=False,
        adapter_mode="capability-only",
        supports_api_key=True,
        supports_base_url=True,
        default_base_url=None,
    ),
}


class WaveLlmProviderConfigService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def config_response(self) -> WaveLlmConfigResponse:
        return WaveLlmConfigResponse(
            enabled=self._settings.wave_llm_enabled,
            config_path=str(self._config_path()),
            defaults=self.effective_defaults(),
            providers=[self.provider_summary(provider) for provider in SUPPORTED_WAVE_LLM_PROVIDERS],
            monitor_preferences=self._monitor_preferences(),
            guardrails=[
                "Provider keys are BYOK inputs owned by the user and are masked in API responses.",
                "Per-wave provider preferences may override the global default provider/model, but never bypass review gating.",
                "Execution budgets, retries, and timeouts stay bounded even when provider settings are updated.",
            ],
            caveats=[WAVE_LLM_CONFIG_STORAGE_CAVEAT],
        )

    def update_defaults(self, request: WaveLlmDefaultsUpdateRequest) -> WaveLlmConfigResponse:
        self._validate_provider(request.default_provider)
        self._validate_limits(
            request_budget=request.request_budget_default,
            max_retries=request.max_retries_default,
            timeout_seconds=request.timeout_seconds_default,
        )
        payload = self._load_payload()
        payload["defaults"] = {
            "default_provider": request.default_provider,
            "default_model": request.default_model.strip() or self._settings.wave_llm_default_model,
            "allow_network_default": request.allow_network_default,
            "request_budget_default": request.request_budget_default,
            "max_retries_default": request.max_retries_default,
            "timeout_seconds_default": request.timeout_seconds_default,
        }
        self._write_payload(payload)
        return self.config_response()

    def update_provider(
        self,
        provider: WaveLlmProvider,
        request: WaveLlmProviderConfigUpdateRequest,
    ) -> WaveLlmConfigResponse:
        self._validate_provider(provider)
        metadata = PROVIDER_METADATA[provider]
        if request.api_key and not metadata.supports_api_key:
            raise ValueError(f"{provider} does not use an API key in this slice.")
        if request.clear_api_key and not metadata.supports_api_key:
            raise ValueError(f"{provider} does not use an API key in this slice.")
        if request.base_url is not None and not metadata.supports_base_url:
            raise ValueError(f"{provider} does not support a configurable base URL.")
        self._validate_limits(
            request_budget=request.request_budget_default,
            max_retries=request.max_retries_default,
            timeout_seconds=request.timeout_seconds_default,
        )

        payload = self._load_payload()
        providers = payload.setdefault("providers", {})
        entry = dict(providers.get(provider, {}))
        if metadata.supports_api_key:
            if request.clear_api_key:
                entry.pop("api_key", None)
            elif request.api_key:
                entry["api_key"] = request.api_key.strip()
        if metadata.supports_base_url:
            entry["base_url"] = _clean_optional_text(request.base_url)
        entry["default_model"] = _clean_optional_text(request.default_model)
        entry["allow_network_default"] = request.allow_network_default
        entry["request_budget_default"] = request.request_budget_default
        entry["max_retries_default"] = request.max_retries_default
        entry["timeout_seconds_default"] = request.timeout_seconds_default
        providers[provider] = _prune_mapping(entry)
        if not providers[provider]:
            providers.pop(provider, None)
        self._write_payload(payload)
        return self.config_response()

    def update_monitor_preference(
        self,
        monitor_id: str,
        request: WaveLlmMonitorPreferenceUpdateRequest,
    ) -> WaveLlmMonitorPreferenceSummary:
        if request.provider is not None:
            self._validate_provider(request.provider)
        self._validate_limits(
            request_budget=request.request_budget,
            max_retries=request.max_retries,
            timeout_seconds=request.timeout_seconds,
        )
        now = _utc_now()
        with session_scope(self._settings.wave_monitor_database_url) as session:
            monitor = session.get(WaveMonitorORM, monitor_id)
            if monitor is None:
                raise ValueError(f"Unknown monitor_id: {monitor_id}")
            row = session.get(WaveLlmMonitorPreferenceORM, monitor_id)
            if row is None:
                row = WaveLlmMonitorPreferenceORM(
                    monitor_id=monitor_id,
                    provider=request.provider,
                    model=_clean_optional_text(request.model),
                    allow_network=request.allow_network,
                    request_budget=request.request_budget,
                    max_retries=request.max_retries,
                    timeout_seconds=request.timeout_seconds,
                    updated_at=now,
                )
                session.add(row)
            else:
                row.provider = request.provider
                row.model = _clean_optional_text(request.model)
                row.allow_network = request.allow_network
                row.request_budget = request.request_budget
                row.max_retries = request.max_retries
                row.timeout_seconds = request.timeout_seconds
                row.updated_at = now
            session.flush()
            return _serialize_monitor_preference(row, monitor.title)

    def effective_defaults(self) -> WaveLlmDefaultsSummary:
        payload = self._load_payload()
        defaults = payload.get("defaults", {})
        return WaveLlmDefaultsSummary(
            default_provider=_coerce_provider(
                defaults.get("default_provider"),
                fallback=self._settings.wave_llm_default_provider,
            ),
            default_model=_clean_required_text(defaults.get("default_model"), self._settings.wave_llm_default_model),
            allow_network_default=_coerce_bool(defaults.get("allow_network_default"), fallback=False),
            request_budget_default=_coerce_non_negative_int(defaults.get("request_budget_default"), fallback=0),
            max_retries_default=_coerce_non_negative_int(
                defaults.get("max_retries_default"),
                fallback=self._settings.wave_llm_max_retries,
            ),
            timeout_seconds_default=_coerce_positive_int(
                defaults.get("timeout_seconds_default"),
                fallback=self._settings.wave_llm_http_timeout_seconds,
            ),
        )

    def provider_summary(self, provider: WaveLlmProvider) -> WaveLlmProviderConfigSummary:
        resolved = self.resolved_provider(provider)
        return WaveLlmProviderConfigSummary(
            provider=resolved.provider,
            configured=resolved.configured,
            key_source=resolved.key_source,
            local=resolved.local,
            adapter_mode=resolved.adapter_mode,
            supports_api_key=resolved.supports_api_key,
            supports_base_url=resolved.supports_base_url,
            env_fallback_configured=resolved.env_fallback_configured,
            masked_secret=resolved.masked_secret,
            base_url=resolved.base_url,
            default_model=resolved.default_model,
            allow_network_default=resolved.allow_network_default,
            request_budget_default=resolved.request_budget_default,
            max_retries_default=resolved.max_retries_default,
            timeout_seconds_default=resolved.timeout_seconds_default,
            caveats=resolved.caveats,
        )

    def resolved_provider(self, provider: WaveLlmProvider) -> ResolvedWaveLlmProviderConfig:
        self._validate_provider(provider)
        metadata = PROVIDER_METADATA[provider]
        payload = self._load_payload()
        entry = payload.get("providers", {}).get(provider, {})
        stored_api_key = _clean_optional_text(entry.get("api_key"))
        stored_base_url = _clean_optional_text(entry.get("base_url"))
        env_api_key = self._settings_value(metadata.settings_api_key_attr)
        env_base_url = self._settings_value(metadata.settings_base_url_attr)
        api_key = stored_api_key or env_api_key
        base_url = stored_base_url or env_base_url or metadata.default_base_url
        env_fallback_configured = bool(env_api_key or env_base_url)
        configured = False
        key_source = "not-configured"
        if provider == "fixture":
            configured = True
            key_source = "built-in"
        elif metadata.supports_api_key and api_key:
            configured = True
            key_source = "runtime-file" if stored_api_key else str(metadata.env_api_key_name or "environment")
        elif metadata.supports_base_url and base_url:
            configured = True
            key_source = "runtime-file" if stored_base_url else str(metadata.env_base_url_name or "built-in")
        caveats: list[str] = []
        if provider != "fixture" and configured:
            caveats.append("Configured status does not validate quota, billing, or provider-side model availability.")
        if metadata.local:
            caveats.append("Local-model paths remain low-trust and must still pass review validation.")
        if metadata.adapter_mode == "capability-only":
            caveats.append("This provider family is configurable, but its generic execution path remains unimplemented.")
        if key_source == "runtime-file":
            caveats.append(WAVE_LLM_CONFIG_STORAGE_CAVEAT)
        return ResolvedWaveLlmProviderConfig(
            provider=provider,
            configured=configured,
            key_source=key_source,
            local=metadata.local,
            adapter_mode=metadata.adapter_mode,
            supports_api_key=metadata.supports_api_key,
            supports_base_url=metadata.supports_base_url,
            env_fallback_configured=env_fallback_configured,
            masked_secret=_mask_secret(api_key) if api_key else None,
            api_key=api_key,
            base_url=base_url,
            default_model=_clean_optional_text(entry.get("default_model")),
            allow_network_default=_coerce_optional_bool(entry.get("allow_network_default")),
            request_budget_default=_coerce_optional_non_negative_int(entry.get("request_budget_default")),
            max_retries_default=_coerce_optional_non_negative_int(entry.get("max_retries_default")),
            timeout_seconds_default=_coerce_optional_positive_int(entry.get("timeout_seconds_default")),
            caveats=caveats,
        )

    def resolve_task_profile(
        self,
        *,
        monitor_id: str,
        requested_provider: WaveLlmProvider | None,
        requested_model: str | None,
    ) -> ResolvedWaveLlmTaskProfile:
        defaults = self.effective_defaults()
        preference = self.monitor_preference(monitor_id)
        provider = requested_provider or preference.provider or defaults.default_provider
        self._validate_provider(provider)
        provider_config = self.resolved_provider(provider)
        model = (
            _clean_optional_text(requested_model)
            or preference.model
            or provider_config.default_model
            or defaults.default_model
        )
        return ResolvedWaveLlmTaskProfile(provider=provider, model=model)

    def resolve_execution_options(
        self,
        *,
        monitor_id: str,
        provider: WaveLlmProvider,
        allow_network: bool | None,
        request_budget: int | None,
        max_retries: int | None,
        timeout_seconds: int | None,
    ) -> ResolvedWaveLlmExecutionOptions:
        defaults = self.effective_defaults()
        preference = self.monitor_preference(monitor_id)
        provider_config = self.resolved_provider(provider)
        resolved_allow_network = (
            allow_network
            if allow_network is not None
            else preference.allow_network
            if preference.allow_network is not None
            else provider_config.allow_network_default
            if provider_config.allow_network_default is not None
            else defaults.allow_network_default
        )
        resolved_request_budget = (
            request_budget
            if request_budget is not None
            else preference.request_budget
            if preference.request_budget is not None
            else provider_config.request_budget_default
            if provider_config.request_budget_default is not None
            else defaults.request_budget_default
        )
        resolved_max_retries = (
            max_retries
            if max_retries is not None
            else preference.max_retries
            if preference.max_retries is not None
            else provider_config.max_retries_default
            if provider_config.max_retries_default is not None
            else defaults.max_retries_default
        )
        resolved_timeout_seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else preference.timeout_seconds
            if preference.timeout_seconds is not None
            else provider_config.timeout_seconds_default
            if provider_config.timeout_seconds_default is not None
            else defaults.timeout_seconds_default
        )
        self._validate_limits(
            request_budget=resolved_request_budget,
            max_retries=resolved_max_retries,
            timeout_seconds=resolved_timeout_seconds,
        )
        return ResolvedWaveLlmExecutionOptions(
            allow_network=resolved_allow_network,
            request_budget=resolved_request_budget,
            max_retries=resolved_max_retries,
            timeout_seconds=resolved_timeout_seconds,
        )

    def monitor_preference(self, monitor_id: str) -> WaveLlmMonitorPreferenceSummary:
        with session_scope(self._settings.wave_monitor_database_url) as session:
            monitor = session.get(WaveMonitorORM, monitor_id)
            title = monitor.title if monitor is not None else monitor_id
            row = session.get(WaveLlmMonitorPreferenceORM, monitor_id)
            if row is None:
                return WaveLlmMonitorPreferenceSummary(
                    monitor_id=monitor_id,
                    monitor_title=title,
                    provider=None,
                    model=None,
                    allow_network=None,
                    request_budget=None,
                    max_retries=None,
                    timeout_seconds=None,
                    updated_at="",
                )
            return _serialize_monitor_preference(row, title)

    def _monitor_preferences(self) -> list[WaveLlmMonitorPreferenceSummary]:
        with session_scope(self._settings.wave_monitor_database_url) as session:
            rows = list(session.query(WaveLlmMonitorPreferenceORM).order_by(WaveLlmMonitorPreferenceORM.updated_at.desc()))
            if not rows:
                return []
            monitor_ids = [row.monitor_id for row in rows]
            titles = {
                monitor.monitor_id: monitor.title
                for monitor in session.query(WaveMonitorORM).filter(WaveMonitorORM.monitor_id.in_(monitor_ids))
            }
            return [
                _serialize_monitor_preference(row, titles.get(row.monitor_id, row.monitor_id))
                for row in rows
            ]

    def _load_payload(self) -> dict[str, object]:
        path = self._config_path()
        if not path.exists():
            return {"version": 1, "defaults": {}, "providers": {}}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"version": 1, "defaults": {}, "providers": {}}
        if not isinstance(payload, dict):
            return {"version": 1, "defaults": {}, "providers": {}}
        defaults = payload.get("defaults")
        providers = payload.get("providers")
        return {
            "version": 1,
            "defaults": defaults if isinstance(defaults, dict) else {},
            "providers": providers if isinstance(providers, dict) else {},
        }

    def _write_payload(self, payload: dict[str, object]) -> None:
        path = self._config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(
            {
                "version": 1,
                "updated_at": _utc_now(),
                "defaults": payload.get("defaults", {}),
                "providers": payload.get("providers", {}),
            },
            indent=2,
            sort_keys=True,
        )
        temp_path = path.with_suffix(path.suffix + ".tmp")
        with os.fdopen(os.open(temp_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temp_path, path)

    def _config_path(self) -> Path:
        runtime_paths = resolve_runtime_paths(self._settings)
        return Path(runtime_paths["user_data_dir"]) / "config" / "wave_llm_provider_config.json"

    def _settings_value(self, attr_name: str | None) -> str | None:
        if not attr_name:
            return None
        value = getattr(self._settings, attr_name, None)
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed or None
        return None

    def _validate_provider(self, provider: str) -> None:
        if provider not in SUPPORTED_WAVE_LLM_PROVIDERS:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _validate_limits(
        self,
        *,
        request_budget: int | None,
        max_retries: int | None,
        timeout_seconds: int | None,
    ) -> None:
        if request_budget is not None and request_budget < 0:
            raise ValueError("request_budget must be zero or greater.")
        if max_retries is not None and max_retries < 0:
            raise ValueError("max_retries must be zero or greater.")
        if timeout_seconds is not None and timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero.")


def _serialize_monitor_preference(
    row: WaveLlmMonitorPreferenceORM,
    monitor_title: str,
) -> WaveLlmMonitorPreferenceSummary:
    return WaveLlmMonitorPreferenceSummary(
        monitor_id=row.monitor_id,
        monitor_title=monitor_title,
        provider=row.provider,  # type: ignore[arg-type]
        model=row.model,
        allow_network=row.allow_network,
        request_budget=row.request_budget,
        max_retries=row.max_retries,
        timeout_seconds=row.timeout_seconds,
        updated_at=row.updated_at,
    )


def _coerce_provider(value: object, *, fallback: str) -> WaveLlmProvider:
    candidate = str(value or fallback).strip()
    if candidate not in SUPPORTED_WAVE_LLM_PROVIDERS:
        candidate = fallback
    return candidate  # type: ignore[return-value]


def _clean_optional_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    trimmed = value.strip()
    return trimmed or None


def _clean_required_text(value: object, fallback: str) -> str:
    return _clean_optional_text(value) or fallback


def _coerce_bool(value: object, *, fallback: bool) -> bool:
    if isinstance(value, bool):
        return value
    return fallback


def _coerce_optional_bool(value: object) -> bool | None:
    return value if isinstance(value, bool) else None


def _coerce_non_negative_int(value: object, *, fallback: int) -> int:
    try:
        candidate = int(value)
    except (TypeError, ValueError):
        return fallback
    return max(0, candidate)


def _coerce_optional_non_negative_int(value: object) -> int | None:
    try:
        candidate = int(value)
    except (TypeError, ValueError):
        return None
    return max(0, candidate)


def _coerce_positive_int(value: object, *, fallback: int) -> int:
    try:
        candidate = int(value)
    except (TypeError, ValueError):
        return fallback
    return candidate if candidate > 0 else fallback


def _coerce_optional_positive_int(value: object) -> int | None:
    try:
        candidate = int(value)
    except (TypeError, ValueError):
        return None
    return candidate if candidate > 0 else None


def _mask_secret(secret: str) -> str:
    if len(secret) <= 8:
        return "*" * len(secret)
    return f"{secret[:3]}***{secret[-4:]}"


def _prune_mapping(value: dict[str, object]) -> dict[str, object]:
    return {
        key: item
        for key, item in value.items()
        if item not in (None, "")
    }


def _utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")
