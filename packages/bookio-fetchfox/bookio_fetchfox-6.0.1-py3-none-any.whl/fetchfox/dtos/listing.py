from datetime import datetime
from typing import List

from fetchfox.apis import price


class ListingDTO:
    def __init__(
        self,
        identifier: str,
        collection_id: str,
        asset_ids: List[str],
        asset_names: List[str],
        listing_id: str,
        marketplace: str,
        price: float,
        currency: str,
        listed_at: datetime,
        listed_by: str = None,
        tx_hash: str = None,
        marketplace_url: str = None,
    ):
        self.identifier: str = identifier
        self.collection_id: str = collection_id
        self.asset_ids: List[str] = asset_ids
        self.asset_names: List[str] = asset_names
        self.listing_id: str = listing_id
        self.marketplace: str = marketplace
        self.price: float = price
        self.currency: str = currency
        self.listed_at: datetime = listed_at
        self.listed_by: str = listed_by
        self.tx_hash: str = tx_hash
        self.marketplace_url: str = marketplace_url

    @property
    def price_str(self) -> str:
        return f"{self.price} {self.currency}"

    @property
    def usd(self) -> float:
        return self.price * price.usd(self.currency)

    @property
    def usd_str(self) -> str:
        return f"{self.usd:0.2f} USD"

    @property
    def first(self) -> str:
        return self.asset_ids[0]

    @property
    def is_bundle(self) -> bool:
        return len(self.asset_ids) > 1

    def __repr__(self) -> str:
        return f"{self.collection_id}/{self.first} x {self.price} {self.currency} ({self.marketplace})"
