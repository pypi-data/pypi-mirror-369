import logging
import os
from typing import Tuple

from fetchfox import rest
from fetchfox.checks import check_str
from fetchfox.constants.blockchains import COINBASE, ETHEREUM, POLYGON

BASE_URL_DEFAULT = "https://deep-index.moralis.io/api"
BASE_URL = os.getenv("MORALISIO_BASE_URL") or BASE_URL_DEFAULT

API_KEY = os.getenv("MORALISIO_API_KEY")

logger = logging.getLogger(__name__)


MAINNET = {
    ETHEREUM: "eth",
    POLYGON: "polygon",
    COINBASE: "base",
}

TESTNET = {
    ETHEREUM: "0xaa36a7",  # sepolia
    POLYGON: "0x13882",  # amoy
    COINBASE: "0x14a34",  # base-sepolia
}


def get(
    service: str,
    blockchain: str,
    params: dict = None,
    version: str = "2.2",
    api_key: str = None,
    preprod: bool = False,
) -> Tuple[dict, int]:
    api_key = api_key or API_KEY
    check_str(api_key, "moralisio.api_key")
    check_str(blockchain, "moralisio.blockchain")

    if preprod:
        chain = TESTNET.get(blockchain)
    else:
        chain = MAINNET.get(blockchain)

    params = params or {}
    params["chain"] = chain

    return rest.get(
        url=f"{BASE_URL}/v{version}/{service}",
        params=params,
        headers={
            "X-API-Key": api_key,
            "Host": "deep-index.moralis.io",
        },
    )
