from __future__ import annotations

import os
import sys
from pathlib import Path

from src.config.settings import Settings


APP_NAME = "11Writer"
SERVER_ROOT = Path(__file__).resolve().parents[2]


def resolve_runtime_paths(settings: Settings) -> dict[str, str]:
    resource_dir = _resolve_dir(settings.app_resource_dir, default=SERVER_ROOT)
    user_data_dir = _resolve_user_data_dir(settings)
    log_dir = _resolve_dir(settings.app_log_dir, default=user_data_dir / "logs")
    cache_dir = _resolve_dir(settings.app_cache_dir, default=user_data_dir / "cache")
    service_artifact_dir = _resolve_dir(
        settings.app_runtime_service_dir,
        default=user_data_dir / "runtime" / "services",
    )
    return {
        "resource_dir": str(resource_dir),
        "user_data_dir": str(user_data_dir),
        "log_dir": str(log_dir),
        "cache_dir": str(cache_dir),
        "service_artifact_dir": str(service_artifact_dir),
    }


def ensure_runtime_service_artifact_dir(
    settings: Settings,
    *,
    platform_name: str,
    create: bool = False,
) -> Path:
    paths = resolve_runtime_paths(settings)
    root = Path(paths["service_artifact_dir"]) / platform_name
    if create:
        root.mkdir(parents=True, exist_ok=True)
    return root


def _resolve_user_data_dir(settings: Settings) -> Path:
    override = settings.app_user_data_dir
    if override:
        return _resolve_dir(override)
    if sys.platform.startswith("win"):
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / APP_NAME
        return Path.home() / "AppData" / "Roaming" / APP_NAME
    if sys.platform.startswith("darwin"):
        return Path.home() / "Library" / "Application Support" / APP_NAME
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home) / APP_NAME
    return Path.home() / ".local" / "share" / APP_NAME


def _resolve_dir(raw: str | os.PathLike[str] | None = None, *, default: Path | None = None) -> Path:
    if raw is None:
        if default is None:
            raise ValueError("A runtime path override or default path is required.")
        path = default
    else:
        path = Path(raw)
    if not path.is_absolute():
        path = (SERVER_ROOT / path).resolve()
    return path
