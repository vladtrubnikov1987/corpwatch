import signal
import time

from repositories.target_repository import target_repository
from services.monitoring_service import monitoring_service
from utils.logger import logger


WORKER_INTERVAL_SECONDS = 10
worker_running = True


def handle_shutdown_signal(signum, frame):
    global worker_running

    logger.info("Worker received shutdown signal: %s", signum)
    worker_running = False


def run_worker():
    logger.info("CorpWatch worker started")

    while worker_running:
        try:
            logger.info("Worker cycle started")

            active_targets = target_repository.get_active_targets()

            logger.info("Worker found %s active targets", len(active_targets))

            for target in active_targets:
                if not worker_running:
                    break

                target_id = target["id"]

                logger.info("Worker checking target_id=%s", target_id)

                try:
                    result = monitoring_service.check_target_now(target_id)

                    logger.info(
                        "Worker check completed. target_id=%s result_type=%s alert_status=%s notification_status=%s",
                        target_id,
                        result.get("result_type"),
                        result.get("alert_status"),
                        result.get("notification_status"),
                    )

                except Exception as error:
                    logger.error(
                        "Worker failed to check target_id=%s error=%s",
                        target_id,
                        error,
                    )

            logger.info("Worker cycle finished")

        except Exception as error:
            logger.error("Worker cycle failed: %s", error)

        time.sleep(WORKER_INTERVAL_SECONDS)

    logger.info("CorpWatch worker stopped")


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_shutdown_signal)
    signal.signal(signal.SIGINT, handle_shutdown_signal)

    run_worker()