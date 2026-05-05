from __future__ import annotations

import json
import sys
from pathlib import Path

from src.config.settings import get_settings
from src.services.media_geolocation_eval_service import MediaGeolocationEvaluationService


def main() -> int:
    settings = get_settings()
    service = MediaGeolocationEvaluationService(settings)
    manifest_path = sys.argv[1] if len(sys.argv) > 1 else None
    if manifest_path is not None and not Path(manifest_path).exists():
        print(json.dumps({"error": f"Manifest not found: {manifest_path}"}, indent=2))
        return 1
    result = service.run_fixture_evaluation(path=manifest_path)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
