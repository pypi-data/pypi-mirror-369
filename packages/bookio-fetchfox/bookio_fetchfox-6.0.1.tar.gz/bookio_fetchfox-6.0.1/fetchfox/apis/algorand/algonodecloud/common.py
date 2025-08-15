import os
from typing import Tuple

from fetchfox import rest

BASE_URL_DEFAULT = "https://mainnet-idx.algonode.cloud"
BASE_URL = os.getenv("ALGONODECLOUD_API_BASE_URL") or BASE_URL_DEFAULT


def get(service: str, params: dict = None, version: int = 2) -> Tuple[dict, int]:
    return rest.get(
        url=f"{BASE_URL}/v{version}/{service}",
        params=params,
    )
