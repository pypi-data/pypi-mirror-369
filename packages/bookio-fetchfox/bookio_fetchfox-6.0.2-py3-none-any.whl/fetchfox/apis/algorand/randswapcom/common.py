import os
from typing import Tuple

from fetchfox import rest

BASE_URL_DEFAULT = "https://randswap.com"
BASE_URL = os.getenv("RANDSWAPCOM_API_BASE_URL") or BASE_URL_DEFAULT


def get(service: str, params: dict = None, version: int = 1) -> Tuple[dict, int]:
    return rest.get(
        url=f"{BASE_URL}/v{version}/{service}",
        params=params,
    )
