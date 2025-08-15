import os
from typing import Tuple

from fetchfox import rest
from fetchfox.checks import check_str

BASE_URL_DEFAULT = "https://mainnet.gomaestro-api.org"
BASE_URL = os.getenv("GOMAESTROORG_BASE_URL") or BASE_URL_DEFAULT

API_KEY = os.getenv("GOMAESTROORG_API_KEY")


def get(service: str, params: dict = None, version: int = 1, api_key: str = None, preprod: bool = False, check: str = None) -> Tuple[dict, int]:
    api_key = api_key or API_KEY
    check_str(api_key, "gomaestroorg.api_key")

    base_url = BASE_URL

    if preprod:
        base_url = base_url.replace("mainnet", "preprod")

    return rest.get(
        url=f"{base_url}/v{version}/{service}",
        params=params,
        headers={
            "api-key": api_key,
        },
        check=check,
    )
