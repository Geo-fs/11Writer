from __future__ import annotations

import argparse
import logging
import time

from sqlmodel import Session

from app.api.deps import db
from app.db.init_db import init_db
from app.scheduler.service import run_scheduler_tick

logger = logging.getLogger(__name__)


def run_loop(interval_seconds: int) -> None:
    init_db(db)
    logger.info("Scheduler worker started with interval_seconds=%s", interval_seconds)
    while True:
        with Session(db.engine) as session:
            result = run_scheduler_tick(session)
            logger.info(
                "scheduler tick: scanned=%s eligible=%s success=%s failed=%s",
                result.scanned_connectors,
                result.eligible_connectors,
                result.successful_runs,
                result.failed_runs,
            )
        time.sleep(interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local 7Po8 scheduler worker loop.")
    parser.add_argument("--interval-seconds", type=int, default=30)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    run_loop(max(5, args.interval_seconds))


if __name__ == "__main__":
    main()
