import logging
import os
from typing import Dict


prefixes: Dict = {
    "auth": os.getenv("AUTH_PREFIX", "/auth"),
    "asset": os.getenv("ASSET_PREFIX", "/asset"),
}


# Configure logging
def get_logger(logger_name: str):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(logger_name)

    return logger
