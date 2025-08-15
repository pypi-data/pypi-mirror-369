from fetchfox.constants.cardano.pools.stuff import STUFF_POOL_FINGERPRINT, STUFF_POOL_ID, STUFF_POOL_NAME
from .base import CardanoPool


class StuffPool(CardanoPool):
    def __init__(self, gomaestroorg_api_key: str = None):
        super().__init__(
            id=STUFF_POOL_ID,
            name=STUFF_POOL_NAME,
            fingerprint=STUFF_POOL_FINGERPRINT,
            gomaestroorg_api_key=gomaestroorg_api_key,
        )
