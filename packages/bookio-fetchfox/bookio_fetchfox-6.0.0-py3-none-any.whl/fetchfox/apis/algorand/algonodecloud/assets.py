import json
from base64 import b64decode
from functools import lru_cache
from typing import Iterable

from fetchfox.checks import check_str
from .common import get
from .schemas import AssetsDataSchema, AssetHolderSchema


@lru_cache(maxsize=None)
def get_data(asset_id: str) -> AssetsDataSchema:
    check_str(asset_id, "algonodecloud.asset_id")

    response, status_code = get(
        service=f"assets/{asset_id}",
    )

    asset = response["asset"]
    return AssetsDataSchema.model_validate(asset)


@lru_cache(maxsize=None)
def get_metadata(asset_id: str) -> dict:
    check_str(asset_id, "algonodecloud.asset_id")

    response, status_code = get(
        f"assets/{asset_id}/transactions",
        params={
            "limit": "1",
            "tx-type": "acfg",
        },
    )

    transaction = response["transactions"][0]

    if "note" in transaction:
        note = b64decode(transaction["note"]).decode("utf-8")
    else:
        note = "{}"

    return json.loads(note)


def get_holders(asset_id: str) -> Iterable[AssetHolderSchema]:
    check_str(asset_id, "algonodecloud.asset_id")

    response, status_code = get(
        service=f"assets/{asset_id}/balances",
        params={
            "currency-greater-than": "0",
        },
    )

    for balance in response.get("balances", []):
        balance["asset-id"] = asset_id

        yield AssetHolderSchema.model_validate(balance)
