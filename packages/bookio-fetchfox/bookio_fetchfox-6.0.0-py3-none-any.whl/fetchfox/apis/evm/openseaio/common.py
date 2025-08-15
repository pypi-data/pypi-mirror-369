import logging
import os
from typing import Tuple

from fetchfox import rest
from fetchfox.checks import check_str
from fetchfox.constants.blockchains import ETHEREUM, POLYGON

BASE_URL_DEFAULT = "https://api.opensea.io"
BASE_URL = os.getenv("OPENSEAIO_BASE_URL") or BASE_URL_DEFAULT

API_KEY = os.getenv("OPENSEAIO_API_KEY")

BLOCKCHAINS = {
    ETHEREUM: "ethereum",
    POLYGON: "matic",
}

logger = logging.getLogger(__name__)


def get(service: str, params: dict = None, version: int = 2, check: str = None, api_key: str = None) -> Tuple[dict, int]:
    api_key = api_key or API_KEY
    check_str(api_key, "openseaio.api_key")

    if version == 1:
        url = f"{BASE_URL}/api/v{version}/{service}"
    else:
        url = f"{BASE_URL}/v{version}/{service}"

    return rest.get(
        url=url,
        headers={
            "X-API-KEY": api_key,
        },
        params=params,
        sleep=2.5,
        check=check,
    )
