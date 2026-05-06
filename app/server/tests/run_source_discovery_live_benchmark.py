from __future__ import annotations

import json

from src.config.settings import Settings
from src.services.source_discovery_eval_service import SourceDiscoveryEvaluationService


def main() -> None:
    settings = Settings(APP_ENV="test")
    service = SourceDiscoveryEvaluationService(settings)
    result = service.run_local_benchmark()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
