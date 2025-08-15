from functools import lru_cache
from typing import Iterable

from fetchfox.checks import check_str
from .common import get
from .schemas import AssetHolderSchema


def get_holders(asset_id: str, api_key: str = None, preprod: bool = False) -> Iterable[AssetHolderSchema]:
    check_str(asset_id, "gomaestroorg.asset_id")

    cursor = None

    while True:
        response, status_code = get(
            service=f"assets/{asset_id}/accounts",
            params={
                "cursor": cursor,
            },
            api_key=api_key,
            preprod=preprod,
        )

        for data in response.get("data", []):
            data["asset_id"] = asset_id
            yield AssetHolderSchema.model_validate(data)

        cursor = response.get("next_cursor")

        if not cursor:
            break


@lru_cache(maxsize=None)
def get_data(asset_id: str, api_key: str = None, preprod: bool = False) -> dict:
    check_str(asset_id, "gomaestroorg.asset_id")

    asset_id = asset_id.strip().lower()

    response, status_code = get(
        service=f"assets/{asset_id}",
        api_key=api_key,
        preprod=preprod,
        check="data",
    )

    cip25_metadata = response["data"]["asset_standards"].get("cip25_metadata")
    cip68_metadata = response["data"]["asset_standards"].get("cip68_metadata")

    metadata = cip68_metadata or cip25_metadata

    if not metadata:
        return None

    metadata["total_supply"] = response["data"].get("total_supply", "1")

    return metadata
