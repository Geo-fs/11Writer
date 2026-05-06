from __future__ import annotations

import json

from src.services.source_discovery_adversarial_eval_service import SourceDiscoveryAdversarialEvaluationService


def main() -> None:
    service = SourceDiscoveryAdversarialEvaluationService()
    result = service.run_fixture_evaluation()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
