from typing import Optional, List, Union

from pydantic import field_validator, Field

from fetchfox.apis.base import BaseModel


class AccountAssetSchema(BaseModel):
    unit: str
    amount: int


class AssetHolderSchema(BaseModel):
    asset_id: str
    account: str
    amount: int

    @field_validator("amount", mode="before")
    def convert_amount(cls, value):
        return int(value)


class PolicyHolderSchema(BaseModel):
    class AccountAssetSchema(BaseModel):
        name: str
        amount: int

        @field_validator("amount", mode="before")
        def convert_amount(cls, value):
            return int(value)

    account: str
    assets: List[AccountAssetSchema]


class CollectionAssetSchema(BaseModel):
    class AssetStandardsSchema(BaseModel):
        cip25_metadata: Optional[dict]
        cip68_metadata: Optional[dict]

    asset_name: str
    total_supply: int

    asset_standards: AssetStandardsSchema

    @field_validator("total_supply", mode="before")
    def convert_total_supply(cls, value):
        return int(value)


class TransactionSchema(BaseModel):
    class InputOutputSchema(BaseModel):
        class AssetSchema(BaseModel):
            unit: str
            amount: int

            @field_validator("amount", mode="before")
            def convert_amount(cls, value):
                return int(value)

        address: str
        assets: List[AssetSchema] = []

    class MetadataSchema(BaseModel):
        class M674Schema(BaseModel):
            msg: Optional[str] = None

            @field_validator("msg", mode="before")
            def ensure_string(cls, value):
                if value is None:
                    return None

                if isinstance(value, list):
                    return " ".join(value)

                return str(value)

        m_674: Optional[Union[M674Schema, str]] = Field(None, alias="674")

    tx_hash: str
    block_timestamp: int
    fee: int

    inputs: List[InputOutputSchema]
    outputs: List[InputOutputSchema]
    metadata: Optional[MetadataSchema] = None


class PoolInformationSchema(BaseModel):
    live_saturation: float
    live_stake: float
    live_delegators: float

    @field_validator("live_saturation", mode="before")
    def convert_live_saturation(cls, value):
        return float(value)

    @field_validator("live_stake", mode="before")
    def convert_live_stake(cls, value):
        return float(value)

    @field_validator("live_delegators", mode="before")
    def convert_live_delegators(cls, value):
        return float(value)


class PoolDelegatorSchema(BaseModel):
    stake_address: str
    amount: float

    @field_validator("amount", mode="before")
    def convert_amount(cls, value):
        return float(value)
