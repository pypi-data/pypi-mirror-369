from typing import Optional, List

from pydantic import field_validator

from fetchfox.apis.base import BaseModel


class AddressesAssetsSchema(BaseModel):
    amount: float
    name: str
    token_address: str
    token_id: str

    @field_validator("token_id", mode="before")
    def convert_token_id(cls, value):
        return str(value)


class AssetHoldersSchema(BaseModel):
    amount: float
    owner_of: str
    token_address: str
    token_id: str

    @field_validator("token_id", mode="before")
    def convert_token_id(cls, value):
        return str(value)


class NftHoldersSchema(BaseModel):
    amount: float
    owner_of: str
    token_address: str
    token_id: str

    @field_validator("token_id", mode="before")
    def convert_token_id(cls, value):
        return str(value)


class WalletTransactionsSchema(BaseModel):
    class Erc20TransfersSchema(BaseModel):
        from_address: str
        to_address: str
        token_decimals: int
        token_symbol: str
        value: float

    class NftTransfersSchema(BaseModel):
        from_address: str
        to_address: str
        amount: float
        token_address: str
        token_id: str

        @field_validator("token_id", mode="before")
        def convert_token_id(cls, value):
            return str(value)

    class NativeTransfersSchema(BaseModel):
        from_address: str
        to_address: str
        decimals: int = 18
        token_symbol: str
        value: float

    hash: str
    summary: Optional[str] = None
    erc20_transfers: List[Erc20TransfersSchema] = None
    nft_transfers: List[NftTransfersSchema] = None
    native_transfers: List[NativeTransfersSchema] = None
