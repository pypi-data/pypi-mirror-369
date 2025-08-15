from functools import lru_cache
from typing import Iterable

from fetchfox.checks import check_str
from . import transactions
from .common import get
from .schemas import TransactionSchema


@lru_cache(maxsize=None)
def get_stake_address(address: str, api_key: str = None, preprod: bool = False) -> str:
    check_str(address, "gomaestroorg.address")

    response, status_code = get(
        service=f"addresses/{address}/decode",
        api_key=api_key,
        preprod=preprod,
    )

    try:
        return response["staking_cred"]["reward_address"]
    except:
        return address


def get_transactions(address: str, last: int = 15, api_key: str = None, preprod: bool = False) -> Iterable[TransactionSchema]:
    response, status_code = get(
        service=f"addresses/{address}/transactions",
        params={
            "count": last,
            "order": "desc",
        },
        api_key=api_key,
        preprod=preprod,
        check="data",
    )

    for tx in response["data"]:
        yield transactions.get_transaction(
            tx["tx_hash"],
            api_key=api_key,
            preprod=preprod,
        )
