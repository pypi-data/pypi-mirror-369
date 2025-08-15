from fetchfox.apis.evm import openseaio
from fetchfox.blockchains.evm import Evm
from fetchfox.constants.blockchains import COINBASE
from fetchfox.constants.currencies import ETH
from fetchfox.helpers.otp import generate_otp


class Coinbase(Evm):
    def __init__(
        self,
        moralisio_api_key: str = None,
        openseaio_api_key: str = None,
        preprod: bool = False,
    ):
        super().__init__(
            name=COINBASE,
            currency=ETH,
            logo="https://s2.coinmarketcap.com/static/img/coins/64x64/27716.png",
            moralisio_api_key=moralisio_api_key,
            openseaio_api_key=openseaio_api_key,
            preprod=preprod,
        )

    def explorer_url(self, *, address: str = None, collection_id: str = None, asset_id: str = None, tx_hash: str = None) -> str:
        if self.preprod:
            basescan_domain = "https://sepolia.basescan.org"
        else:
            basescan_domain = "https://basescan.org"

        if address:
            return f"{basescan_domain}/address/{address.lower()}"

        if asset_id:
            assert collection_id
            return f"{basescan_domain}/token/{collection_id.lower()}?a={asset_id}"

        if collection_id:
            return f"{basescan_domain}/token/{collection_id.lower()}"

        if tx_hash:
            return f"{basescan_domain}/tx/{tx_hash.lower()}"

        return None

    def marketplace_url(self, *, collection_id: str = None, asset_id: str = None) -> str:
        if asset_id:
            assert collection_id
            return f"https://opensea.io/assets/base/{collection_id.lower()}/{asset_id}"

        if collection_id:
            slug = openseaio.get_collection_slug(
                contract_address=collection_id,
                blockchain=self.name,
                api_key=self.openseaio_api_key,
            )

            return f"https://opensea.io/collection/{slug}"

        return None

    # others
    def get_otp(self) -> float:
        return float(f"0.000{generate_otp()}")

    # sanity
    def sanity_check(self) -> bool:
        if self.preprod:
            collection_id, asset_id = "0x77ba80dcc4cc43a28ea6f26eb5e5eade57ab0e5f", "7"
            asset_number = 9
        else:
            collection_id, asset_id = "0x8c1f34bcb76449cebf042cfe8293cd8265ae6802", "6"
            asset_number = 90

        asset_name = "Artificial Intelligence For Dummies"

        self.validate_sanity_check(collection_id, asset_id, asset_name, asset_number)
