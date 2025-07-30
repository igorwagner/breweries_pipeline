"""Logger setup for consistent debug and info output across the project."""

import logging

logger = logging.getLogger("breweries_datalake_logger")

if not logger.hasHandlers():
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s — %(levelname)s — %(name)s — %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
