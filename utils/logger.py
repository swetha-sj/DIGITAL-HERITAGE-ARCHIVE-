"""
Digital Heritage Archive - Logging and Audit Trail Utility
Provides structured logging for archival operations, ingestion runs, and searches.
"""

import logging
from pathlib import Path
from config import BASE_DIR

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "heritage_archive.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("DigitalHeritageArchive")


def get_logger(name: str = "DHA") -> logging.Logger:
    """Returns a named logger instance."""
    return logging.getLogger(name)
