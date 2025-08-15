from typing import Iterable

from fetchfox.checks import check_str
from .common import get
from .schemas import NftHoldersSchema


def get_assets(contract_address: str, blockchain: str, api_key: str = None, preprod: bool = False) -> Iterable[str]:
    check_str(contract_address, "moralisio.contract_address")
    contract_address = contract_address.strip().lower()

    cursor = ""

    while True:
        response, status_code = get(
            service=f"nft/{contract_address}",
            params={
                "cursor": cursor,
                "format": "decimal",
                "normalizeMetadata": "false",
            },
            blockchain=blockchain,
            api_key=api_key,
            preprod=preprod,
        )

        for item in response.get("result", []):
            yield item["token_id"]

        if not response.get("cursor"):
            break

        cursor = response["cursor"]


def get_holders(contract_address: str, blockchain: str, api_key: str = None, preprod: bool = False) -> Iterable[NftHoldersSchema]:
    check_str(contract_address, "moralisio.contract_address")
    contract_address = contract_address.strip().lower()

    cursor = ""

    while True:
        response, status_code = get(
            service=f"nft/{contract_address}/owners",
            params={
                "cursor": cursor,
            },
            blockchain=blockchain,
            api_key=api_key,
            preprod=preprod,
        )

        yield from map(
            NftHoldersSchema.model_validate,
            response.get("result", []),
        )

        cursor = response.get("cursor")

        if not cursor:
            break


def get_supply(contract_address: str, blockchain: str, api_key: str = None, preprod: bool = False) -> int:
    check_str(contract_address, "moralisio.contract_address")
    contract_address = contract_address.strip().lower()

    response, status_code = get(
        service=f"nft/{contract_address}/stats",
        blockchain=blockchain,
        api_key=api_key,
        preprod=preprod,
    )

    if response is None:
        return -1

    return int(response.get("total_tokens", -1))
