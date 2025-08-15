import base64
from functools import lru_cache

from fetchfox.checks import check_str
from fetchfox.constants.cardano.policies import ADA_HANDLE_POLICY_ID
from . import accounts
from . import assets


@lru_cache(maxsize=None)
def get_handle(stake_address: str, api_key: str = None, preprod: bool = False) -> str:
    check_str(stake_address, "gomaestroorg.stake_address")

    holdings = accounts.get_assets(
        stake_address,
        api_key=api_key,
        policy_id=ADA_HANDLE_POLICY_ID,
        preprod=preprod,
    )

    handles = []

    for holding in holdings:
        asset_id = holding.unit
        asset_id = asset_id.replace(f"{ADA_HANDLE_POLICY_ID}000de140", "")  # CIP-68
        asset_id = asset_id.replace(ADA_HANDLE_POLICY_ID, "")  # CIP-25

        asset_name = bytes.fromhex(asset_id).decode()
        handles.append(asset_name)

    if not handles:
        return None

    return sorted(handles, key=len)[0]


@lru_cache(maxsize=None)
def resolve_handle(handle: str, api_key: str = None, preprod: bool = False) -> str:
    check_str(handle, "gomaestroorg.handle")

    handle = handle.lower()

    if handle.startswith("$"):
        handle = handle[1:]

    wallet = resolve_cip25_handle(handle, api_key, preprod=preprod)

    if wallet:
        return wallet

    return resolve_cip68_handle(handle, api_key, preprod=preprod)


def resolve_cip25_handle(handle: str, api_key: str = None, preprod: bool = False) -> str:
    check_str(handle, "gomaestroorg.handle")

    encoded_name = base64.b16encode(handle.encode()).decode("utf-8")

    asset_id = f"{ADA_HANDLE_POLICY_ID}{encoded_name}".lower()
    holders = list(assets.get_holders(asset_id, api_key, preprod=preprod))

    if not holders:
        return None

    return holders[0].account


def resolve_cip68_handle(handle: str, api_key: str = None, preprod: bool = False) -> str:
    check_str(handle, "gomaestroorg.handle")

    encoded_name = base64.b16encode(handle.encode()).decode("utf-8")

    asset_id = f"{ADA_HANDLE_POLICY_ID}000de140{encoded_name}".lower()
    holder = list(assets.get_holders(asset_id, api_key, preprod=preprod))

    if not holder:
        return None

    return holder[0].account
