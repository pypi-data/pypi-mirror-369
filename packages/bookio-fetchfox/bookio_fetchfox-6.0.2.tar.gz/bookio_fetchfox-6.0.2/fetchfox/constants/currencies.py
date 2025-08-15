from fetchfox.constants.algorand.basics import ALGO
from fetchfox.constants.cardano.basics import ADA
from fetchfox.constants.cardano.tokens.beard import BEARD_TOKEN_SYMBOL as BEARD
from fetchfox.constants.cardano.tokens.book import BOOK_TOKEN_SYMBOL as BOOK
from fetchfox.constants.cardano.tokens.charles import CHARLES_TOKEN_SYMBOL as CHARLES
from fetchfox.constants.cardano.tokens.stuff import STUFF_TOKEN_SYMBOL as STUFF
from fetchfox.constants.ethereum.basics import ETH
from fetchfox.constants.fiat import USD
from fetchfox.constants.polygon.basics import MATIC, POL

CRYPTOS = [
    # cryptocurrencies
    ALGO,
    ADA,
    ETH,
    MATIC,
    POL,
    # cardano tokens
    BEARD,
    BOOK,
    CHARLES,
    STUFF,
]

FIATS = [
    USD,
]
