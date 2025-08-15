from datetime import datetime
from enum import Enum
from typing import List

from fetchfox.apis import price


class SaleType(str, Enum):
    OFFER = "OFFER"
    COLLECTION_OFFER = "INSTANT"
    PURCHASE = "PURCHASE"
    CREDIT_CARD = "CREDIT_CARD"


class SaleDTO:
    def __init__(
        self,
        identifier: str,
        collection_id: str,
        asset_ids: List[str],
        asset_names: List[str],
        tx_hash: str,
        marketplace: str,
        price: float,
        currency: str,
        confirmed_at: datetime,
        type: SaleType = SaleType.PURCHASE,
        bulk_size: int = 1,
        sale_id: str = None,
        sold_by: str = None,
        bought_by: str = None,
        marketplace_url: str = None,
        explorer_url: str = None,
    ):
        self.identifier: str = identifier
        self.collection_id: str = collection_id
        self.asset_ids: List[str] = asset_ids
        self.asset_names: List[str] = asset_names
        self.marketplace: str = marketplace
        self.price: float = price
        self.currency: str = currency
        self.confirmed_at: datetime = confirmed_at
        self.type: SaleType = type
        self.bulk_size: int = bulk_size
        self.tx_hash: str = tx_hash
        self.sale_id: str = sale_id
        self.sold_by: str = sold_by
        self.bought_by: str = bought_by
        self.marketplace_url: str = marketplace_url
        self.explorer_url: str = explorer_url

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
