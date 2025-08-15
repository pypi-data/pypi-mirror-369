import typing

if typing.TYPE_CHECKING:
    from .listing import ListingDTO


class FloorDTO:
    def __init__(
        self,
        listing: "ListingDTO",
        listing_count: int,
    ):
        self.listing: "ListingDTO" = listing
        self.listing_count: int = listing_count

    def __repr__(self) -> str:
        return str(self.listing)
