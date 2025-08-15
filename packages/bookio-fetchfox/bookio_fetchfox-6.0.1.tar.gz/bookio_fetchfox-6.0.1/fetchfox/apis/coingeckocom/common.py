import logging
import os
import time
from typing import Tuple

from fetchfox import rest

FREE = "free"
DEMO = "demo"
PRO = "pro"

API_KEY = os.getenv("COINGECKO_API_KEY") or os.getenv("COINGECKOCOM_API_KEY")
API_KEY_TYPE = os.getenv("COINGECKO_API_KEY_TYPE")

if API_KEY_TYPE is None:
    if API_KEY:
        API_KEY_TYPE = DEMO
    else:
        API_KEY_TYPE = FREE


if API_KEY_TYPE in PRO:
    BASE_URL = "https://pro-api.coingecko.com/api"
    RATE_LIMIT = 500
    HEADERS = {
        "x-cg-pro-api-key": API_KEY,
    }
elif API_KEY_TYPE in DEMO:
    BASE_URL = "https://api.coingecko.com/api"
    RATE_LIMIT = 30
    HEADERS = {
        "x-cg-demo-api-key": API_KEY,
    }
else:
    BASE_URL = "https://api.coingecko.com/api"
    RATE_LIMIT = 5
    HEADERS = {}


logger = logging.getLogger(__name__)


def get(service: str, params: dict = None, version: int = 3) -> Tuple[dict, int]:
    logger.debug("calling %s [%s]", service, API_KEY_TYPE)

    time.sleep(60 / RATE_LIMIT)

    return rest.get(
        url=f"{BASE_URL}/v{version}/{service}",
        headers=HEADERS,
        params=params,
    )
