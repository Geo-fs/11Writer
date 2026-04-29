from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve

from src.reference.ingest.dataset_manifest import DatasetManifest


def prepare_source(manifest: DatasetManifest, staging_root: Path) -> Path:
    if manifest.source_mode == "local":
        if manifest.source_path is None:
            raise ValueError(f"Local manifest {manifest.name} requires source_path.")
        return manifest.source_path
    if manifest.source_mode != "remote" or not manifest.remote_url:
        raise ValueError(f"Unsupported source mode for manifest {manifest.name}.")

    target_dir = staging_root / manifest.name / manifest.version
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = manifest.expected_files[0] if manifest.expected_files else Path(manifest.remote_url).name or "dataset.bin"
    target_file = target_dir / filename
    if not target_file.exists():
        urlretrieve(manifest.remote_url, target_file)
    return target_dir
