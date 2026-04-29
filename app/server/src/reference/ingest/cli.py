from __future__ import annotations

import argparse
from pathlib import Path

from src.reference.db import session_scope
from src.reference.ingest.dataset_manifest import DatasetManifest
from src.reference.ingest.parsers import PARSERS
from src.reference.ingest.staging import prepare_source
from src.reference.repository import ReferenceRepository


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest canonical geospatial reference datasets.")
    parser.add_argument("dataset", choices=sorted(PARSERS.keys()))
    parser.add_argument("source_path", help="Directory containing dataset files.")
    parser.add_argument("--database-url", default="sqlite:///./data/reference.db")
    parser.add_argument("--version", default="local")
    parser.add_argument("--coverage", default="global-core")
    parser.add_argument("--checksum", default=None)
    parser.add_argument("--source-mode", choices=["local", "remote"], default="local")
    parser.add_argument("--remote-url", default=None)
    parser.add_argument("--staging-root", default="./data/reference_staging")
    args = parser.parse_args()

    manifest = DatasetManifest(
        name=args.dataset,
        version=args.version,
        coverage=args.coverage,
        checksum=args.checksum,
        source_mode=args.source_mode,
        precedence=10,
        parser_name=args.dataset,
        source_path=Path(args.source_path) if args.source_mode == "local" else None,
        expected_files=_expected_files(args.dataset),
        remote_url=args.remote_url,
    )
    source_path = prepare_source(manifest, Path(args.staging_root))
    records = PARSERS[args.dataset](source_path, args.version)
    with session_scope(args.database_url) as session:
        repository = ReferenceRepository(session)
        count = repository.upsert_records(
            records=records,
            dataset_name="faa-fixes" if args.dataset == "fixes" else args.dataset,
            dataset_version=args.version,
            coverage=args.coverage,
            checksum=manifest.checksum,
            source_path=str(source_path),
            notes=f"Loaded via {args.dataset} CLI importer.",
        )
    print(f"Ingested {count} records from {args.dataset}.")


if __name__ == "__main__":
    main()


def _expected_files(dataset_name: str) -> tuple[str, ...]:
    if dataset_name == "ourairports":
        return ("airports.csv", "runways.csv", "navaids.csv")
    if dataset_name == "places":
        return ("regions.geojson", "places.json")
    if dataset_name == "fixes":
        return ("fixes.csv",)
    if dataset_name == "airport-codes":
        return ("airport-codes.json",)
    return ()
