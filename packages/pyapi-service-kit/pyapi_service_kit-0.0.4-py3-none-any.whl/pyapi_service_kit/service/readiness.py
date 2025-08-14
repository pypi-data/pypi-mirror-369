import logging
import os
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def mark_service_ready(
    readiness_file_path: str = os.getenv("HEALTH_READY_FILE", "/tmp/ready"),
):
    try:
        readiness_file = Path(readiness_file_path)
        readiness_file.parent.mkdir(parents=True, exist_ok=True)
        readiness_file.write_text("ready", encoding="utf-8")
    except Exception as e:
        LOGGER.warning(f"Failed to write readiness file: {e}")
