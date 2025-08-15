import os

from fetchfox import rest
from fetchfox.checks import check_str

BASE_URL_DEFAULT = "https://api-us.dexhunterv3.app"
BASE_URL = os.getenv("DEXHUNTERIO_API_BASE_URL") or BASE_URL_DEFAULT

PARTNER_CODE = os.getenv("DEXHUNTERIO_PARTNER_CODE")


def get(service: str, params: dict = None, partner_code: str = None) -> dict:
    partner_code = partner_code or PARTNER_CODE
    check_str(partner_code, "dexhunterio.partner_code")

    response, _ = rest.get(
        url=f"{BASE_URL}/{service}",
        params=params,
        headers={
            "X-Partner-Id": partner_code,
        },
    )

    return response


def post(service: str, body: dict, params: dict = None, partner_code: str = None) -> dict:
    partner_code = partner_code or PARTNER_CODE
    check_str(partner_code, "dexhunterio.partner_code")

    response, _ = rest.post(
        url=f"{BASE_URL}/{service}",
        params=params,
        body=body,
        headers={
            "X-Partner-Id": partner_code,
        },
    )

    return response
