import logging
from datetime import datetime
from typing import Iterable

from cachetools.func import ttl_cache

from fetchfox.constants.currencies import ALGO, ADA, BOOK, ETH, MATIC, POL, STUFF, USD
from .common import get
from .schemas import CoinExchangeHistorySchema

logger = logging.getLogger(__name__)

IDS = {
    ALGO: "algorand",
    ADA: "cardano",
    BOOK: "book-2",
    ETH: "ethereum",
    MATIC: "matic-network",
    POL: "polygon-ecosystem-token",
    STUFF: "book-2",
}


@ttl_cache(ttl=60 * 60)
def get_exchange(crypto: str, fiat: str = USD, date: datetime = None) -> float:
    crypto, fiat = crypto.strip().upper(), fiat.strip().lower()
    coin_id = IDS[crypto]

    logger.info("fetching exchange %s/%s (%s)", crypto, fiat, coin_id)

    if date is None:
        response, status_code = get(
            service="simple/price",
            params={
                "ids": coin_id,
                "vs_currencies": fiat,
            },
        )

        return response[coin_id][fiat]
    else:
        date = date or datetime.now()

        response, status_code = get(
            service=f"coins/{coin_id}/history",
            params={
                "date": date.strftime("%d-%m-%Y"),
                "localization": "false",
            },
        )

        market_data = response.get("market_data")

        if not market_data:
            return None

        return market_data["current_price"][fiat]


@ttl_cache(ttl=60 * 60)
def get_ath(crypto: str, fiat: str = USD) -> float:
    crypto, fiat = crypto.strip().upper(), fiat.strip().lower()
    coin_id = IDS[crypto]

    logger.info("fetching ath for %s/%s (%s)", crypto, fiat, coin_id)

    response, status_code = get(
        service=f"coins/{coin_id}",
    )

    return response["market_data"]["ath"][fiat]


def get_exchange_history(crypto: str, fiat: str = USD, days: int = 7) -> Iterable[CoinExchangeHistorySchema]:
    crypto, fiat = crypto.strip().upper(), fiat.strip().lower()
    coin_id = IDS[crypto]

    logger.info("fetching exchange history of %s/%s (%s)", crypto, fiat, coin_id)

    response, status_code = get(
        service=f"coins/{coin_id}/market_chart",
        params={
            "vs_currency": fiat,
            "days": days,
        },
    )

    for timestampe, price in response["prices"]:
        yield CoinExchangeHistorySchema(
            crypto=crypto,
            fiat=fiat,
            timestamp=timestampe,
            price=price,
        )
