from typing import Iterable

from fetchfox.checks import check_str
from .common import get
from .schemas import AddressesAssetsSchema


def get_balance(address: str, blockchain: str, api_key: str = None, preprod: bool = False) -> float:
    check_str(address, "moralisio.address")
    address = address.strip().lower()

    response, status_code = get(
        service=f"{address}/balance",
        blockchain=blockchain,
        api_key=api_key,
        preprod=preprod,
    )

    return int(response["balance"]) / 10**18


def get_assets(address: str, blockchain: str, api_key: str = None, preprod: bool = False) -> Iterable[AddressesAssetsSchema]:
    check_str(address, "moralisio.address")
    address = address.strip().lower()

    cursor = ""

    while True:
        response, status_code = get(
            service=f"{address}/nft",
            params={
                "cursor": cursor,
            },
            blockchain=blockchain,
            api_key=api_key,
            preprod=preprod,
        )

        for asset in response.get("result", []):
            if not asset.get("name"):
                continue

            yield AddressesAssetsSchema.model_validate(asset)

        if not response.get("cursor"):
            break

        cursor = response["cursor"]
