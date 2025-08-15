from typing import Iterable

from fetchfox.checks import check_str
from .common import get
from .schemas import (
    AccountAssetsSchema,
    AccountTransactionSchema,
)


def get_assets(address: str) -> Iterable[AccountAssetsSchema]:
    check_str(address, "algonodecloud.address")
    address = address.strip().upper()

    next_token = None

    while True:
        response, status_code = get(
            service=f"accounts/{address}/assets",
            params={
                "include-all": "false",
                "next": next_token,
            },
        )

        yield from filter(
            lambda a: a.amount > 0,
            map(
                AccountAssetsSchema.model_validate,
                response["assets"],
            ),
        )

        next_token = response.get("next-token")

        if not next_token:
            break


def get_created_assets(address: str) -> Iterable[int]:
    check_str(address, "algonodecloud.address")
    address = address.strip().upper()

    next_token = None

    while True:
        response, status_code = get(
            service=f"accounts/{address}/created-assets",
            params={
                "include-all": "false",
                "next": next_token,
            },
        )

        for asset in response["assets"]:
            yield str(asset["index"])

        next_token = response.get("next-token")

        if not next_token:
            break


def get_created_supply(creator_address: str) -> int:
    return len(list(get_created_assets(creator_address)))


def get_balance(address: str) -> float:
    check_str(address, "algonodecloud.address")
    address = address.strip().upper()

    response, status_code = get(
        service=f"accounts/{address}",
        params={
            "include-all": "false",
        },
    )

    return int(response["account"]["amount"]) / 10**6


def get_transactions(address: str) -> Iterable[AccountTransactionSchema]:
    check_str(address, "algonodecloud.address")
    address = address.strip().upper()

    next_token = None

    while True:
        response, status_code = get(
            service=f"accounts/{address}/transactions",
            params={
                "next": next_token,
            },
        )

        yield from map(
            AccountTransactionSchema.model_validate,
            response["transactions"],
        )

        next_token = response.get("next-token")

        if not next_token:
            break
