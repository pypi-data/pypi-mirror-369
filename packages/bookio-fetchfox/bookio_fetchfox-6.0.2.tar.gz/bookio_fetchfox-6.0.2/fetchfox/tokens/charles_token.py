from fetchfox.constants.cardano.tokens.charles import (
    CHARLES_TOKEN_ASSET_ID,
    CHARLES_TOKEN_ASSET_NAME,
    CHARLES_TOKEN_POLICY_ID,
    CHARLES_TOKEN_FINGERPRINT,
    CHARLES_TOKEN_SYMBOL,
)

from .base import CardanoToken


class CharlesToken(CardanoToken):
    def __init__(self, dexhunterio_partner_code: str = None):
        super().__init__(
            asset_id=CHARLES_TOKEN_ASSET_ID,
            asset_name=CHARLES_TOKEN_ASSET_NAME,
            fingerprint=CHARLES_TOKEN_FINGERPRINT,
            policy_id=CHARLES_TOKEN_POLICY_ID,
            symbol=CHARLES_TOKEN_SYMBOL,
            decimals=0,
            taptools_pair_id="bfcbf9a63822d7bc1f12297bfe625432a9486ebf4a05d4925fa158cf8c352a8f",
            dexhunterio_partner_code=dexhunterio_partner_code,
        )
