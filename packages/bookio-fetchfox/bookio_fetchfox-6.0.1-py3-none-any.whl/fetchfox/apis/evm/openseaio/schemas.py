from typing import List

from pydantic import Field

from fetchfox.apis.base import BaseModel


class CollectionsListingsSchema(BaseModel):
    class PriceSchema(BaseModel):
        class CurrentSchema(BaseModel):
            currency: str
            decimals: int
            value: float

        current: CurrentSchema

    class ProtocolDataSchema(BaseModel):
        class ParametersSchema(BaseModel):
            class OfferSchema(BaseModel):
                identifier_or_criteria: str = Field(..., alias="identifierOrCriteria")
                token: str

            offerer: str
            offer: List[OfferSchema]
            start_time: int = Field(..., alias="startTime")

        parameters: ParametersSchema

    order_hash: str
    price: PriceSchema
    protocol_data: ProtocolDataSchema


class EventsSalesSchema(BaseModel):
    class NftSchema(BaseModel):
        contract: str
        identifier: str
        name: str

    class PaymentSchema(BaseModel):
        decimals: int
        quantity: float
        symbol: str

    buyer: str
    closing_date: int
    seller: str
    transaction: str
    nft: NftSchema
    payment: PaymentSchema
