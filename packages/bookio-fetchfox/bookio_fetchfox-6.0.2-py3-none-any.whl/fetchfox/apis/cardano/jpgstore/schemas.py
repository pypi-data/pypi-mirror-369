from typing import Optional, List

from pydantic import field_validator

from fetchfox.apis.base import BaseModel


class PolicyListing(BaseModel):
    class BundledAsset(BaseModel):
        asset_id: str
        display_name: str

    asset_id: str
    confirmed_at: str
    display_name: str
    tx_hash: str
    listing_id: int
    listed_at: str
    price_lovelace: int
    listing_type: str
    bundled_assets: Optional[List[BundledAsset]] = None

    @field_validator("price_lovelace", mode="before")
    def convert_price_lovelace(cls, value):
        return int(value)

    @property
    def url(self) -> str:
        return f"https://jpg.store/asset/{self.asset_id}"


class CollectionSale(BaseModel):
    class ListingFromTxHistory(BaseModel):
        class BundledAsset(BaseModel):
            asset_id: str
            display_name: str

        bundled_assets: Optional[List[BundledAsset]] = None

    tx_hash: str
    asset_id: str
    display_name: str
    bulk_size: int = 1
    action: str
    seller_address: str
    signer_address: str
    amount_lovelace: int
    confirmed_at: Optional[str] = None
    created_at: str

    listing_from_tx_history: Optional[ListingFromTxHistory] = None

    @field_validator("amount_lovelace", mode="before")
    def convert_amount_lovelace(cls, value):
        return int(value)

    @field_validator("bulk_size", mode="before")
    def ensure_bulk_size(cls, value):
        if value is None:
            return 1

        return int(value)

    @property
    def url(self) -> str:
        return f"https://jpg.store/asset/{self.asset_id}"
