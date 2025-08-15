from typing import List, Tuple

from cachetools.func import ttl_cache

from fetchfox.apis import coingeckocom
from fetchfox.apis import price
from fetchfox.apis.cardano import dexhunterio
from fetchfox.constants.currencies import ADA


class CardanoToken:
    def __init__(
        self,
        asset_id: str,
        asset_name: str,
        fingerprint: str,
        policy_id: str,
        symbol: str,
        decimals: int = 6,
        coingecko_id: str = None,
        taptools_pair_id: str = None,
        dexhunterio_partner_code: str = None,
    ):
        self.asset_id: str = asset_id
        self.asset_name: str = asset_name
        self.fingerprint: str = fingerprint
        self.policy_id: str = policy_id
        self.symbol: str = symbol
        self.decimals: int = decimals

        self.coingecko_id: str = coingecko_id
        self.taptools_pair_id: str = taptools_pair_id
        self.dexhunterio_partner_code = dexhunterio_partner_code

    @property
    @ttl_cache(ttl=30)
    def ada(self) -> float:
        return dexhunterio.get_asset_average_price(
            self.asset_id,
            partner_code=self.dexhunterio_partner_code,
        )

    @property
    @ttl_cache(ttl=30)
    def usd(self) -> float:
        return price.usd(ADA) * self.ada

    @property
    @ttl_cache(ttl=30)
    def ath_usd(self) -> float:
        return price.ath_usd(self.symbol)

    def history(self, days: int = 7) -> List[Tuple[int, float]]:
        for exchange in coingeckocom.get_exchange_history(self.symbol, days=days):
            yield exchange.timestamp, exchange.price

    @property
    def cardanoscan_url(self):
        return f"https://cardanoscan.io/token/{self.asset_id}"

    @property
    def cexplorer_url(self):
        return f"https://cexplorer.io/asset/{self.fingerprint}"

    @property
    def coingecko_url(self):
        return f"https://www.coingecko.com/en/coins/{self.coingecko_id}"

    @property
    def dexhunter_url(self):
        return f"https://app.dexhunter.io/trends?asset={self.asset_id}&status=COMPLETED"

    @property
    def minswap_url(self):
        return f"https://app.minswap.org/swap?currencySymbolA={self.policy_id}&tokenNameA={self.asset_name}&currencySymbolB=&tokenNameB="

    @property
    def taptools_url(self):
        return f"https://www.taptools.io/charts/token/f5808c2c990d86da54bfc97d89cee6efa20cd8461616359478d96b4c.{self.taptools_pair_id}"
