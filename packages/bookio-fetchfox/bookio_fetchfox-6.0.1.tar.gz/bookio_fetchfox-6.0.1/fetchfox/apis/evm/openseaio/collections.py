import logging
from functools import lru_cache
from typing import Iterable

from fetchfox.checks import check_str
from .common import get, BLOCKCHAINS
from .schemas import CollectionsListingsSchema

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def get_slug(contract_address: str, blockchain: str, api_key: str = None) -> str:
    check_str(contract_address, "openseaio.contract_address")
    contract_address = contract_address.strip().lower()

    check_str(blockchain, "openseaio.blockchain")
    blockchain: str = BLOCKCHAINS.get(blockchain, blockchain)

    logger.info("fetching slug for %s (%s)", contract_address, blockchain)

    response, status_code = get(
        service=f"chain/{blockchain}/contract/{contract_address}",
        api_key=api_key,
        check="collection",
    )

    return response["collection"]


def get_listings(contract_address: str, blockchain: str, slug: str = None, api_key: str = None) -> Iterable[CollectionsListingsSchema]:
    check_str(contract_address, "openseaio.contract_address")
    contract_address = contract_address.strip().lower()

    check_str(blockchain, "openseaio.blockchain")

    if not slug:
        slug = get_slug(contract_address, blockchain, api_key=api_key)

    cursor = ""

    while True:
        response, status_code = get(
            service=f"listings/collection/{slug}/all",
            params={
                "next": cursor,
            },
            api_key=api_key,
        )

        yield from map(
            CollectionsListingsSchema.model_validate,
            response.get("listings", []),
        )

        cursor = response.get("next")

        if not cursor:
            break
