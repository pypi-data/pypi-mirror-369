from pydantic import Field, field_validator

from fetchfox.apis.base import BaseModel


class CreatorListingSchema(BaseModel):
    asset_id: str = Field(..., alias="assetId")
    price: float
    seller_address: str = Field(..., alias="sellerAddress")
    timestamp: int

    @field_validator("asset_id", mode="before")
    def convert_asset_id(cls, value):
        return str(value)

    @property
    def url(self) -> str:
        return f"https://randgallery.com/algo-collection/?address={self.asset_id}"
