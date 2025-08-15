import logging
from datetime import datetime
from typing import Iterable, Optional, Tuple

import pytz
from cachetools.func import ttl_cache

from fetchfox.apis.algorand import algonodecloud, nfdomains, randswapcom
from fetchfox.blockchains.base import Blockchain
from fetchfox.constants.blockchains import ALGORAND
from fetchfox.constants.currencies import ALGO
from fetchfox.constants.marketplaces import RANDGALLERY_COM
from fetchfox.dtos import (
    AssetDTO,
    FloorDTO,
    HoldingDTO,
    ListingDTO,
    SaleDTO,
    TransactionAssetDTO,
    TransactionDTO,
    TransactionInputOutputDTO,
)
from fetchfox.helpers.otp import generate_otp
from . import utils
from .exceptions import (
    InvalidAlgorandAccountException,
    InvalidAlgorandAssetIdException,
    InvalidAlgorandCollectionIdException,
)

logger = logging.getLogger(__name__)


class Algorand(Blockchain):
    def __init__(self):
        super().__init__(
            name=ALGORAND,
            currency=ALGO,
            logo="https://s2.coinmarketcap.com/static/img/coins/64x64/4030.png",
        )

    # checks
    def check_account(self, account: str, exception: bool = True) -> bool:
        valid = utils.is_account(account)

        if not valid and exception:
            raise InvalidAlgorandAccountException(account)

        return valid

    def check_asset_id(self, asset_id: str, exception: bool = True) -> bool:
        valid = utils.is_asset_id(asset_id)

        if not valid and exception:
            raise InvalidAlgorandAssetIdException(asset_id)

        return valid

    def check_collection_id(self, collection_id: str, exception: bool = True) -> bool:
        valid = utils.is_address(collection_id)

        if not valid and exception:
            raise InvalidAlgorandCollectionIdException(collection_id)

        return valid

    # url builders
    def explorer_url(self, *, address: str = None, collection_id: str = None, asset_id: str = None, tx_hash: str = None) -> str:
        if address:
            return f"https://allo.info/account/{address.upper()}"

        if asset_id:
            return f"https://allo.info/asset/{asset_id}/nft"

        if collection_id:
            return f"https://allo.info/account/{collection_id.upper()}"

        if tx_hash:
            return f"https://allo.info/tx/{tx_hash.upper()}"

        return None

    def marketplace_url(self, *, collection_id: str = None, asset_id: str = None) -> str:
        if asset_id:
            return f"https://www.randgallery.com/algo-collection/?address={asset_id}"

        if collection_id:
            return f"https://randgallery.com/algo-collection/?address={collection_id}"

        return None

    # accounts
    @ttl_cache(ttl=600)
    def get_account_main_address(self, account: str, exception: bool = False) -> Optional[str]:
        if not self.check_account(account, exception=exception):
            return None

        resolved = self.resolve_account_name(account)

        return resolved or account

    def get_account_name(self, account: str) -> str:
        if utils.is_nf_domain(account):
            return account

        if utils.is_address(account):
            return nfdomains.get_nf_domain(account)

        return None

    def resolve_account_name(self, name: str) -> str:
        if utils.is_nf_domain(name):
            return nfdomains.resolve_nf_domain(name)

        return None

    # account attributes
    def get_account_assets(self, account: str, collection_id: str = None) -> Iterable[HoldingDTO]:
        address = self.get_account_main_address(account, exception=True)

        for holding in algonodecloud.get_account_assets(address):
            yield HoldingDTO(
                collection_id=None,
                asset_id=holding.asset_id,
                address=account,
                amount=holding.amount,
            )

    def get_account_balance(self, account: str) -> Tuple[float, str]:
        address = self.get_account_main_address(account, exception=True)

        balance = algonodecloud.get_account_balance(address)

        return balance, self.currency

    def get_account_transactions(self, account: str, last: int = 10) -> Iterable[TransactionDTO]:
        address = self.get_account_main_address(account, exception=True)

        for index, transaction in enumerate(algonodecloud.get_account_transactions(address)):
            if index >= last:
                break

            if transaction.tx_type == "pay":
                amount = transaction.payment_transaction.amount / 10**6
                receiver = transaction.payment_transaction.receiver
                unit = self.currency
            elif transaction.tx_type == "axfer":
                amount = transaction.asset_transfer_transaction.amount
                receiver = transaction.asset_transfer_transaction.receiver
                unit = transaction.asset_transfer_transaction.asset_id
            else:
                continue

            yield TransactionDTO(
                blockchain=self.name,
                address=address,
                tx_hash=transaction.id,
                message=transaction.note,
                inputs=[
                    TransactionInputOutputDTO(
                        address=transaction.sender,
                        assets=[
                            TransactionAssetDTO(
                                amount=amount,
                                unit=unit,
                            ),
                        ],
                    ),
                ],
                outputs=[
                    TransactionInputOutputDTO(
                        address=receiver,
                        assets=[
                            TransactionAssetDTO(
                                amount=amount,
                                unit=unit,
                            ),
                        ],
                    ),
                ],
            )

    # assets
    def get_asset(self, collection_id: str, asset_id: str, fetch_metadata: bool = True, *args, **kwargs) -> AssetDTO:
        if collection_id:
            self.check_collection_id(collection_id)

        self.check_asset_id(asset_id)

        asset_data = algonodecloud.get_asset_data(asset_id)

        if fetch_metadata:
            metadata = algonodecloud.get_asset_metadata(asset_id)
            metadata["name"] = asset_data.params.name
        else:
            metadata = {}

        return AssetDTO(
            collection_id=asset_data.params.creator,
            asset_id=asset_id,
            metadata=metadata,
        )

    def get_asset_holders(self, collection_id: str, asset_id: str, *args, **kwargs) -> Iterable[HoldingDTO]:
        self.check_collection_id(collection_id)
        self.check_asset_id(asset_id)

        for holder in algonodecloud.get_asset_holders(asset_id):
            yield HoldingDTO(
                collection_id=collection_id,
                asset_id=holder.asset_id,
                address=holder.address,
                amount=holder.amount,
            )

    # collections
    def get_collection_assets(self, collection_id: str, fetch_metadata: bool = True, *args, **kwargs) -> Iterable[AssetDTO]:
        self.check_collection_id(collection_id)

        collection_assets = algonodecloud.get_account_created_assets(collection_id)

        for asset_id in collection_assets:
            if fetch_metadata:
                yield self.get_asset(
                    collection_id=collection_id,
                    asset_id=asset_id,
                )
            else:
                yield AssetDTO(
                    collection_id=collection_id,
                    asset_id=asset_id,
                    metadata={},
                )

    def get_collection_floor(self, collection_id: str, *args, **kwargs) -> FloorDTO:
        self.check_collection_id(collection_id)

        floor = None
        count = 0

        for listing in self.get_collection_listings(collection_id):
            count += 1

            if floor is None:
                floor = listing
            elif listing.usd < floor.usd:
                floor = listing

        return FloorDTO(
            listing=floor,
            listing_count=count,
        )

    def get_collection_listings(self, collection_id: str, *args, **kwargs) -> Iterable[ListingDTO]:
        self.check_collection_id(collection_id)

        for listing in randswapcom.get_creator_listings(collection_id):
            asset_id = str(listing.asset_id)
            asset_ids = [asset_id]
            asset_names = [""]

            listed_at = datetime.fromtimestamp(
                listing.timestamp // 1000,
            ).replace(
                tzinfo=pytz.UTC,
            )

            yield ListingDTO(
                identifier=listing.timestamp,
                collection_id=collection_id,
                asset_ids=asset_ids,
                asset_names=asset_names,
                listing_id=listing.timestamp,
                marketplace=RANDGALLERY_COM,
                price=listing.price,
                currency=ALGO,
                listed_at=listed_at,
                listed_by=listing.seller_address,
                marketplace_url=listing.url,
            )

    def get_collection_sales(self, collection_id: str, *args, **kwargs) -> Iterable[SaleDTO]:
        return []

    def get_collection_holders(self, collection_id: str, *args, **kwargs) -> Iterable[HoldingDTO]:
        self.check_collection_id(collection_id)

        for asset in self.get_collection_assets(collection_id, fetch_metadata=False):
            yield from self.get_asset_holders(collection_id, asset.asset_id)

    def get_collection_supply(self, collection_id: str, *args, **kwargs) -> int:
        self.check_collection_id(collection_id)

        return algonodecloud.get_account_created_supply(
            creator_address=collection_id,
        )

    # others
    def get_otp(self) -> float:
        return float(f"0.{generate_otp()}")

    def verify_otp(self, account: str, otp: float) -> TransactionDTO:
        return super().verify_otp(account.upper(), otp)

    # sanity
    def sanity_check(self) -> bool:
        collection_id = "W2FPJKZZ6QP4PPAOJZWEUMMA372FF3MJD3PY4GNBZTTR3XKG464INIXMIQ"

        asset_id = "1180518311"
        asset_name, asset_number = "Foundations", 471

        self.validate_sanity_check(collection_id, asset_id, asset_name, asset_number)
