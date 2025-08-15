import os
from typing import Tuple

from fetchfox import rest

BASE_URL_DEFAULT = "https://server.jpgstoreapis.com"
BASE_URL = os.getenv("JPGSTORE_BASE_URL") or BASE_URL_DEFAULT


def get(service: str, params: dict = None, headers: dict = None) -> Tuple[dict, int]:
    return rest.get(
        url=f"{BASE_URL}/{service}",
        params=params,
        headers=headers,
        sleep=5,
    )
