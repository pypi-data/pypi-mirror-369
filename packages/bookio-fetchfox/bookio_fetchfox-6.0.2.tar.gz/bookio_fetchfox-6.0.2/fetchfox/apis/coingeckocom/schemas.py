from fetchfox.apis.base import BaseModel


class CoinExchangeHistorySchema(BaseModel):
    crypto: str
    fiat: str
    timestamp: int
    price: float
