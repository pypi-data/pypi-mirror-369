from fetchfox.constants.cardano.tokens.beard import (
    BEARD_TOKEN_ASSET_ID,
    BEARD_TOKEN_ASSET_NAME,
    BEARD_TOKEN_POLICY_ID,
    BEARD_TOKEN_FINGERPRINT,
    BEARD_TOKEN_SYMBOL,
)

from .base import CardanoToken


class BeardToken(CardanoToken):
    def __init__(self, dexhunterio_partner_code: str = None):
        super().__init__(
            asset_id=BEARD_TOKEN_ASSET_ID,
            asset_name=BEARD_TOKEN_ASSET_NAME,
            fingerprint=BEARD_TOKEN_FINGERPRINT,
            policy_id=BEARD_TOKEN_POLICY_ID,
            symbol=BEARD_TOKEN_SYMBOL,
            decimals=0,
            taptools_pair_id="52bd1e5a642e2141e8fb7ea6fa996960bc91db0b040c6d35013cf3efecac2dfc",
            dexhunterio_partner_code=dexhunterio_partner_code,
        )
