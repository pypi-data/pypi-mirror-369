from fetchfox.constants.cardano.tokens.stuff import (
    STUFF_TOKEN_ASSET_ID,
    STUFF_TOKEN_ASSET_NAME,
    STUFF_TOKEN_COINGECKO_ID,
    STUFF_TOKEN_POLICY_ID,
    STUFF_TOKEN_FINGERPRINT,
    STUFF_TOKEN_SYMBOL,
)

from .base import CardanoToken


class StuffToken(CardanoToken):
    def __init__(self, dexhunterio_partner_code: str = None):
        super().__init__(
            asset_id=STUFF_TOKEN_ASSET_ID,
            asset_name=STUFF_TOKEN_ASSET_NAME,
            fingerprint=STUFF_TOKEN_FINGERPRINT,
            policy_id=STUFF_TOKEN_POLICY_ID,
            symbol=STUFF_TOKEN_SYMBOL,
            decimals=6,
            coingecko_id=STUFF_TOKEN_COINGECKO_ID,
            taptools_pair_id="b68d128216cd07ee83667f1f5d2b65999b034161d88fada290eb5a9a6960c456",
            dexhunterio_partner_code=dexhunterio_partner_code,
        )
