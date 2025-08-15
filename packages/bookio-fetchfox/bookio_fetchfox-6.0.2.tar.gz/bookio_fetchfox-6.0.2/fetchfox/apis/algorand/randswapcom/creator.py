from typing import Iterable

from fetchfox.checks import check_str
from .common import get
from .schemas import CreatorListingSchema


def get_listings(creator_address: str) -> Iterable[CreatorListingSchema]:
    check_str(creator_address, "randswapcom.creator_address")
    creator_address = creator_address.strip().upper()

    response, status_code = get(
        service=f"listings/creator/{creator_address}",
    )

    yield from map(
        CreatorListingSchema.model_validate,
        response,
    )
