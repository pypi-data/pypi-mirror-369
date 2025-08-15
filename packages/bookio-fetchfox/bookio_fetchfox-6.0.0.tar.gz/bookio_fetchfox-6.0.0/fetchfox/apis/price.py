from fetchfox.apis import coingeckocom
from fetchfox.constants.currencies import USD


def usd(crypto: str) -> float:
    return coingeckocom.get_exchange(crypto, fiat=USD)


def ath_usd(crypto: str) -> float:
    return coingeckocom.get_ath(crypto, fiat=USD)
