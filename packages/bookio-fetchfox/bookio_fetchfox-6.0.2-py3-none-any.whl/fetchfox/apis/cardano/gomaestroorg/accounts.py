from typing import Iterable, Tuple

from fetchfox.checks import check_str
from . import addresses
from .common import get
from .schemas import AccountAssetSchema, TransactionSchema


def get_assets(stake_address: str, policy_id: str = None, api_key: str = None, preprod: bool = False) -> Iterable[AccountAssetSchema]:
    check_str(stake_address, "gomaestroorg.stake_address")
    stake_address = stake_address.strip().lower()

    if policy_id:
        policy_id = policy_id.strip().lower()

    cursor = None

    while True:
        response, status_code = get(
            service=f"accounts/{stake_address}/assets",
            params={
                "cursor": cursor,
                "policy": policy_id,
            },
            api_key=api_key,
            preprod=preprod,
            check="data",
        )

        yield from map(
            AccountAssetSchema.model_validate,
            response.get("data", []),
        )

        cursor = response.get("next_cursor")

        if not cursor:
            break


def get_balance(stake_address: str, api_key: str = None, preprod: bool = False) -> float:
    check_str(stake_address, "gomaestroorg.stake_address")
    stake_address = stake_address.strip().lower()

    response, status_code = get(
        service=f"accounts/{stake_address}",
        api_key=api_key,
        preprod=preprod,
    )

    return response["data"]["total_balance"] / 10**6


def get_addresses(stake_address: str, api_key: str = None, preprod: bool = False) -> Iterable[str]:
    response, status_code = get(
        service=f"accounts/{stake_address}/addresses",
        api_key=api_key,
        preprod=preprod,
    )

    yield from response["data"]


def get_transactions(stake_address: str, last: int = 15, api_key: str = None, preprod: bool = False) -> Iterable[Tuple[str, TransactionSchema]]:
    for address in get_addresses(stake_address, api_key=api_key, preprod=preprod):
        for tx in addresses.get_transactions(address, last, api_key=api_key, preprod=preprod):
            yield address, tx
