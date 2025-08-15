from typing import Optional

from fetchfox.checks import check_str
from .common import get


def get_price(contract_address: str, blockchain: str, api_key: str = None, preprod: bool = False) -> Optional[float]:
    check_str(contract_address, "moralisio.contract_address")
    contract_address = contract_address.strip().lower()

    response, status_code = get(
        service=f"erc20/{contract_address}/price",
        blockchain=blockchain,
        api_key=api_key,
        preprod=preprod,
    )

    native_price = response.get("nativePrice")

    if not native_price:
        return None

    value = float(native_price["value"])
    decimals = native_price["decimals"]

    return value / 10**decimals
