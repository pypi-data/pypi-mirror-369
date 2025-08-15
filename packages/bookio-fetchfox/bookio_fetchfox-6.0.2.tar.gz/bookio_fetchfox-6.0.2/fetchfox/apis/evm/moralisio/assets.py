import json
from functools import lru_cache
from typing import Iterable

from fetchfox.apis import pinatacloud
from fetchfox.checks import check_str
from .common import get
from .schemas import AssetHoldersSchema


@lru_cache(maxsize=None)
def get_data(contract_address: str, asset_id: str, blockchain: str, api_key: str = None, preprod: bool = False) -> dict:
    check_str(contract_address, "moralisio.contract_address")
    contract_address = contract_address.strip().lower()

    check_str(asset_id, "moralisio.asset_id")

    response, status_code = get(
        service=f"nft/{contract_address}/{asset_id}",
        blockchain=blockchain,
        api_key=api_key,
        preprod=preprod,
    )

    if status_code == 404:
        raise Exception(f"{contract_address}/{asset_id} doesn't exist")

    if response.get("metadata"):  # metadata is cached by moralis
        metadata = json.loads(response["metadata"])
    else:
        # trigger metadata resync on moralis
        resync_metadata(contract_address, asset_id, blockchain, api_key)

        # fetch metadata from book.io's ipfs node
        token_uri = response["token_uri"].split("ipfs/")[-1]
        metadata = pinatacloud.get_metadata(token_uri)

    metadata["attributes"].update(metadata["extraAttributes"])
    response["metadata"] = metadata

    return response


def resync_metadata(contract_address: str, asset_id: str, blockchain: str, api_key: str = None, preprod: bool = False):
    check_str(contract_address, "moralisio.contract_address")
    contract_address = contract_address.strip().lower()

    check_str(asset_id, "moralisio.asset_id")

    response, status_code = get(
        service=f"nft/{contract_address}/{asset_id}/metadata/resync",
        params={
            "flag": "uri",
            "mode": "sync",
        },
        blockchain=blockchain,
        api_key=api_key,
        preprod=preprod,
    )

    if status_code == 404:
        raise ValueError(f"{contract_address}/{asset_id} doesn't exist")

    return response.get("status")


def get_holders(contract_address: str, asset_id: str, blockchain: str, api_key: str = None, preprod: bool = False) -> Iterable[AssetHoldersSchema]:
    check_str(contract_address, "moralisio.contract_address")
    contract_address = contract_address.strip().lower()

    check_str(asset_id, "moralisio.asset_id")

    response, status_code = get(
        service=f"nft/{contract_address}/{asset_id}/owners",
        blockchain=blockchain,
        api_key=api_key,
        preprod=preprod,
    )

    yield from map(
        AssetHoldersSchema.model_validate,
        response.get("result", []),
    )
