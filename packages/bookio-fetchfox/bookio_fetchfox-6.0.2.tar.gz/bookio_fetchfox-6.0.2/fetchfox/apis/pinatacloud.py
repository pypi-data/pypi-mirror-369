import os

from fetchfox import rest

BASE_URL_DEFAULT = "https://book.mypinata.cloud/ipfs"
BASE_URL = os.getenv("PINATACLOUD_BASE_URL") or BASE_URL_DEFAULT


def get_metadata(uri: str) -> dict:
    uri = uri.replace("ipfs://", "")

    response, status_code = rest.get(
        url=f"{BASE_URL}/{uri}",
    )

    return response
