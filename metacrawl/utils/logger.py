import logging
import sys
from datetime import datetime
from pathlib import Path
from metacrawl.config.settings import settings


def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger based on the application settings.

    - Logs to stdout (console).
    - Logs to a date-stamped file under the configured log directory
      (e.g. ``logs/metacrawl_2026-04-18.log``).
    - The log directory is created automatically if it does not exist.
    - A new file is created each day; old files are kept as-is.
    - Appends to the file on each startup - safe for multiple processes
      and editors holding the file open on Windows.
    """
    logger = logging.getLogger(name)

    # Only configure if it hasn't been configured yet to avoid duplicate logs
    if not logger.handlers:
        level = getattr(logging, settings.log_level.upper(), logging.INFO)
        logger.setLevel(level)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # ── Console handler ──────────────────────────────────────────
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # ── File handler (date-stamped, no rotation rename needed) ───
        log_dir = Path(settings.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        log_file = log_dir / f"metacrawl_{today}.log"

        file_handler = logging.FileHandler(
            filename=log_file,
            mode="a",
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.propagate = False

    return logger
