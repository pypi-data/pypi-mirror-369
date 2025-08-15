from typing import Optional

from fetchfox.checks import check_str
from .common import get


def get_average_price(asset_id: str, partner_code: str = None) -> Optional[float]:
    check_str(asset_id, "dexhunterio.asset_id")

    response = get(
        service=f"swap/averagePrice/{asset_id}/ADA",
        partner_code=partner_code,
    )

    if response is None:
        return None

    return response.get("price_ba")
