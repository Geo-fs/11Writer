from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.reference.schemas import ReferenceRecord


@dataclass(frozen=True)
class DatasetManifest:
    name: str
    version: str
    coverage: str
    checksum: str | None
    source_mode: str
    precedence: int
    parser_name: str
    source_path: Path | None
    expected_files: tuple[str, ...] = ()
    remote_url: str | None = None


@dataclass(frozen=True)
class IngestedDataset:
    manifest: DatasetManifest
    records: list[ReferenceRecord]
