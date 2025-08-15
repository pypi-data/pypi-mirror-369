from fetchfox.apis.evm import openseaio
from fetchfox.blockchains.evm import Evm
from fetchfox.constants.blockchains import ETHEREUM
from fetchfox.constants.currencies import ETH
from fetchfox.helpers.otp import generate_otp


class Ethereum(Evm):
    def __init__(
        self,
        moralisio_api_key: str = None,
        openseaio_api_key: str = None,
        preprod: bool = False,
    ):
        super().__init__(
            name=ETHEREUM,
            currency=ETH,
            logo="https://s2.coinmarketcap.com/static/img/coins/64x64/1027.png",
            moralisio_api_key=moralisio_api_key,
            openseaio_api_key=openseaio_api_key,
            preprod=preprod,
        )

    def explorer_url(self, *, address: str = None, collection_id: str = None, asset_id: str = None, tx_hash: str = None) -> str:
        if self.preprod:
            etherscan_domain = "https://sepolia.etherscan.io"
        else:
            etherscan_domain = "https://etherscan.io"

        if address:
            return f"{etherscan_domain}/address/{address.lower()}"

        if asset_id:
            assert collection_id
            return f"{etherscan_domain}/token/{collection_id.lower()}?a={asset_id}"

        if collection_id:
            return f"{etherscan_domain}/token/{collection_id.lower()}"

        if tx_hash:
            return f"{etherscan_domain}/tx/{tx_hash.lower()}"

        return None

    def marketplace_url(self, *, collection_id: str = None, asset_id: str = None) -> str:
        if asset_id:
            assert collection_id
            return f"https://opensea.io/assets/ethereum/{collection_id.lower()}/{asset_id}"

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
            collection_id = "0x391dda9478f8ef4c066b5bde30ac43543dcdd499"
            asset_id = "0"
        else:
            collection_id = "0x5592e2022691a9850d8acbf243416099e6fb34dd"
            asset_id = "39"

        asset_name, asset_number = "The Wizard of Oz", 101

        self.validate_sanity_check(collection_id, asset_id, asset_name, asset_number)
