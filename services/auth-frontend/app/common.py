import logging
import os
from typing import Dict, Optional
import re


# Configure logging
def get_logger(logger_name: str):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(logger_name)

    return logger


logger = get_logger(__name__)


def get_prefix(key: str, default_val: str = "") -> str:
    val = os.getenv(key, default_val).strip()
    if val[0] == "/":
        matches: Optional[re.Match[str]] = re.search(r"^\/*([a-zA-Z0-9\_]+)$", val)

        if matches is not None:
            match = matches.groups()[0]
            logger.info(f"matches found in '{val}', return '/{match}'")
            return f"/{match}"

    return val


prefixes: Dict = {
    "auth": get_prefix("AUTH_PREFIX", "auth"),
    "asset": get_prefix("ASSET_PREFIX", "asset"),
    "notifications": get_prefix("NOTIFICATIONS_PREFIX", "//notifications"),
}
