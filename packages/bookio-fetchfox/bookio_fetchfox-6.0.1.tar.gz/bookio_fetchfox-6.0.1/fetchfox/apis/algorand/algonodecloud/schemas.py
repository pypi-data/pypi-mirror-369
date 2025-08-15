from base64 import b64decode
from typing import Optional

from pydantic import Field, field_validator

from fetchfox.apis.base import BaseModel


class AccountAssetsSchema(BaseModel):
    amount: int
    asset_id: str = Field(..., alias="asset-id")

    @field_validator("asset_id", mode="before")
    def convert_asset_id(cls, value):
        return str(value)


class AssetsDataSchema(BaseModel):
    class AssetDataParamsSchema(BaseModel):
        creator: str
        name: str

    index: str
    params: AssetDataParamsSchema

    @field_validator("index", mode="before")
    def convert_index(cls, value):
        return str(value)


class AssetHolderSchema(BaseModel):
    address: str
    amount: int
    asset_id: str = Field(..., alias="asset-id")

    @field_validator("asset_id", mode="before")
    def convert_asset_id(cls, value):
        return str(value)


class AccountTransactionSchema(BaseModel):
    class AssetTransferTransactionSchema(BaseModel):
        amount: float
        asset_id: str = Field(..., alias="asset-id")
        receiver: str

        @field_validator("asset_id", mode="before")
        def convert_asset_id(cls, value):
            return str(value)

    class PaymentTransactionSchema(BaseModel):
        amount: float
        receiver: str

    id: str
    note: Optional[str] = None
    sender: str
    tx_type: str = Field(..., alias="tx-type")
    asset_transfer_transaction: Optional[AssetTransferTransactionSchema] = Field(None, alias="asset-transfer-transaction")
    payment_transaction: Optional[PaymentTransactionSchema] = Field(None, alias="payment-transaction")

    @field_validator("note", mode="before")
    def decode_note(cls, value):
        if value is None:
            return None

        return b64decode(value).decode("utf-8")
