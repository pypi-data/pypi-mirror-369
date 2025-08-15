import logging
import warnings
from datetime import datetime
from typing import Iterable, List, Optional, Tuple

import pytz
from cachetools.func import ttl_cache

from fetchfox.apis.cardano import dexhunterio
from fetchfox.apis.cardano import gomaestroorg, jpgstore
from fetchfox.blockchains.base import Blockchain
from fetchfox.constants.blockchains import CARDANO
from fetchfox.constants.cardano.ranks import CNFT_RANKS
from fetchfox.constants.currencies import ADA
from fetchfox.constants.marketplaces import JPG_STORE
from fetchfox.dtos import (
    AssetDTO,
    FloorDTO,
    HoldingDTO,
    ListingDTO,
    RankDTO,
    SaleDTO,
    SaleType,
    TransactionAssetDTO,
    TransactionDTO,
    TransactionInputOutputDTO,
)
from fetchfox.helpers.otp import generate_otp
from . import utils
from .exceptions import (
    InvalidCardanoAccountException,
    InvalidCardanoAssetIdException,
    InvalidCardanoCollectionIdException,
)
from ..exceptions import UnavailableMetadataException

WINTER_NFT_ADDRESS = "addr1qxnrv2quqxhvwxtxmygsmkufph4kjju6j5len7k2ljslpz8ql7k7gehlfvj6ektgu9ns8yx8epcp66337khxeq82rpgqe6lqyk"
SHELLY_EPOCH = 1596491091
SHELLY_SLOT = 4924800

logger = logging.getLogger(__name__)


class Cardano(Blockchain):
    def __init__(
        self,
        preprod: bool = False,
        gomaestroorg_api_key: str = None,
        dexhunterio_partner_code: str = None,
    ):
        super().__init__(
            name=CARDANO,
            currency=ADA,
            logo="https://s2.coinmarketcap.com/static/img/coins/64x64/2010.png",
            preprod=preprod,
        )

        self.gomaestroorg_api_key: str = gomaestroorg_api_key
        self.dexhunterio_partner_code: str = dexhunterio_partner_code

    # checks
    def check_account(self, account: str, exception: bool = True) -> bool:
        if self.preprod:
            valid = utils.is_preprod_account(account)
        else:
            valid = utils.is_account(account)

        if not valid and exception:
            raise InvalidCardanoAccountException(account)

        return valid

    def check_asset_id(self, asset_id: str, exception: bool = True) -> bool:
        valid = utils.is_asset_id(asset_id)

        if not valid and exception:
            raise InvalidCardanoAssetIdException(asset_id)

        return valid

    def check_collection_id(self, collection_id: str, exception: bool = True) -> bool:
        valid = utils.is_policy_id(collection_id)

        if not valid and exception:
            raise InvalidCardanoCollectionIdException(collection_id)

        return valid

    # url builders
    def explorer_url(self, *, address: str = None, collection_id: str = None, asset_id: str = None, tx_hash: str = None) -> str:
        if address:
            return f"https://pool.pm/{address.lower()}"

        if asset_id:
            return f"https://cardanoscan.io/token/{asset_id.lower()}"

        if collection_id:
            return f"https://pool.pm/policy/{collection_id.lower()}"

        if tx_hash:
            return f"https://cardanoscan.io/transaction/{tx_hash.lower()}"

        return None

    def marketplace_url(self, collection_id: str = None, asset_id: str = None) -> str:
        if asset_id:
            return f"https://www.jpg.store/asset/{asset_id.lower()}"

        if collection_id:
            return f"https://jpg.store/collection/{collection_id.lower()}"

        return None

    # accounts
    def get_account_stake_address(self, account: str) -> str:
        warnings.deprecated("cardano.get_account_stake_address is deprecated, please use cardano.get_account_main_address instead")

        return self.get_account_main_address(account)

    @ttl_cache(ttl=600)
    def get_account_main_address(self, account: str, exception: bool = False) -> Optional[str]:
        if not self.check_account(account, exception=exception):
            return None

        is_stake_address = False

        if self.preprod:
            if utils.is_preprod_stake_address(account):
                is_stake_address = True
        else:
            if utils.is_stake_address(account):
                is_stake_address = True

        if is_stake_address:
            return account

        is_address = False

        if self.preprod:
            if utils.is_preprod_address(account):
                is_address = True
        else:
            if utils.is_address(account):
                is_address = True

        if is_address:
            return gomaestroorg.get_address_stake_address(
                account,
                api_key=self.gomaestroorg_api_key,
                preprod=self.preprod,
            )

        if utils.is_ada_handle(account):
            resolution = gomaestroorg.resolve_handle(
                account,
                api_key=self.gomaestroorg_api_key,
                preprod=self.preprod,
            )

            return resolution

        return None

    def get_account_name(self, account: str) -> str:
        if utils.is_ada_handle(account):
            return account

        stake_address = self.get_account_main_address(account)

        return gomaestroorg.get_handle(
            stake_address,
            api_key=self.gomaestroorg_api_key,
            preprod=self.preprod,
        )

    def resolve_account_name(self, name: str) -> str:
        if not utils.is_ada_handle(name):
            return None

        resolution = gomaestroorg.resolve_handle(
            name,
            api_key=self.gomaestroorg_api_key,
            preprod=self.preprod,
        )

        if not resolution:
            return None

        return resolution["stake_address"]

    def format_account(self, account: str) -> str:
        self.check_account(account, exception=True)

        handle = self.get_account_name(account)

        if handle:
            punycode = handle.encode().decode("idna")

            if handle != punycode:
                return f"{punycode} (${handle})"

            return f"${handle}"

        return super().format_account(account)

    # account attributes
    def get_account_assets(self, account: str, collection_id: str = None) -> Iterable[HoldingDTO]:
        stake_address = self.get_account_main_address(account, exception=True)

        if collection_id is not None:
            self.check_collection_id(collection_id)

        account_assets = gomaestroorg.get_account_assets(
            stake_address,
            policy_id=collection_id,
            api_key=self.gomaestroorg_api_key,
            preprod=self.preprod,
        )

        for account_asset in account_assets:
            asset_id = account_asset.unit
            amount = account_asset.amount

            policy_id, _, _ = utils.split_asset_id(asset_id)

            yield HoldingDTO(
                collection_id=policy_id,
                asset_id=asset_id,
                address=stake_address,
                amount=amount,
            )

    def get_account_balance(self, account: str) -> Tuple[float, str]:
        stake_address = self.get_account_main_address(account, exception=True)

        balance = gomaestroorg.get_account_balance(
            stake_address,
            api_key=self.gomaestroorg_api_key,
            preprod=self.preprod,
        )

        return balance, self.currency

    def get_account_transactions(self, account: str, last: int = 10) -> Iterable[TransactionDTO]:
        def parse_input_output(items: list) -> Iterable[TransactionInputOutputDTO]:
            for item in items:
                item_address = item.address
                item_assets = []

                for asset in item.assets:
                    unit = asset.unit
                    amount = asset.amount

                    if unit == "lovelace":
                        unit = self.currency
                        amount = amount / 10**6

                    item_assets.append(
                        TransactionAssetDTO(
                            amount=amount,
                            unit=unit,
                        )
                    )

                yield TransactionInputOutputDTO(
                    address=item_address,
                    assets=item_assets,
                )

        stake_address = self.get_account_main_address(account, exception=True)

        txs = []

        transactions = gomaestroorg.get_account_transactions(
            stake_address,
            api_key=self.gomaestroorg_api_key,
            preprod=self.preprod,
        )

        for address, tx in transactions:
            txs.append((address, tx))

        sorted_transactions = list(
            sorted(
                txs,
                key=lambda x: x[1].block_timestamp,
                reverse=True,
            )
        )

        for address, tx in sorted_transactions[:last]:
            message = None

            if tx.metadata:
                if tx.metadata.m_674:
                    if tx.metadata.m_674.msg:
                        if isinstance(tx.metadata.m_674.msg, list):
                            message = "\n".join(tx.metadata.m_674.msg)
                        elif isinstance(tx.metadata.m_674.msg, str):
                            message = tx.metadata.m_674.msg
                        else:
                            message = ""

            inputs = list(parse_input_output(tx.inputs))
            outputs = list(parse_input_output(tx.outputs))

            yield TransactionDTO(
                blockchain=self.name,
                address=stake_address,
                tx_hash=tx.tx_hash,
                message=message,
                inputs=inputs,
                outputs=outputs,
            )

    # assets
    def get_asset(self, collection_id: str, asset_id: str, *args, **kwargs) -> AssetDTO:
        if collection_id is None:
            collection_id = asset_id[:56]

        self.check_collection_id(collection_id)
        self.check_asset_id(asset_id)

        asset_data = gomaestroorg.get_asset_data(
            asset_id,
            api_key=self.gomaestroorg_api_key,
            preprod=self.preprod,
        )

        if not asset_data:
            raise UnavailableMetadataException(asset_id)

        return AssetDTO(
            collection_id=collection_id,
            asset_id=asset_id,
            metadata=asset_data,
            supply=int(asset_data.get("total_supply", 1)),
        )

    def get_asset_holders(self, collection_id: str, asset_id: str, *args, **kwargs) -> Iterable[HoldingDTO]:
        self.check_collection_id(collection_id)
        self.check_asset_id(asset_id)

        asset_owners = gomaestroorg.get_asset_holders(
            asset_id,
            api_key=self.gomaestroorg_api_key,
            preprod=self.preprod,
        )

        for owner in asset_owners:
            yield HoldingDTO(
                collection_id=collection_id,
                asset_id=owner.asset_id,
                address=owner.account,
                amount=owner.amount,
            )

    def get_asset_rank(self, collection_id: str, asset_id: str, *args, **kwargs) -> RankDTO:
        self.check_collection_id(collection_id)
        self.check_asset_id(asset_id)

        _, _, decoded_asset_name = utils.split_asset_id(asset_id)

        if collection_id not in CNFT_RANKS:
            return None

        if not decoded_asset_name:
            return None

        if decoded_asset_name not in CNFT_RANKS[collection_id]:
            return None

        digits = "".join((c for c in decoded_asset_name if c.isdigit()))

        if not digits:
            return None

        number = int(digits)

        return RankDTO(
            collection_id=collection_id,
            number=number,
            asset_id=asset_id,
            rank=CNFT_RANKS[collection_id][decoded_asset_name],
        )

    # collections
    def get_collection_assets(
        self,
        collection_id: str,
        discriminator: str = None,
        fetch_metadata: bool = True,
        *args,
        **kwargs,
    ) -> Iterable[AssetDTO]:
        self.check_collection_id(collection_id)

        if discriminator:
            discriminator = discriminator.lower()

        collection_assets = gomaestroorg.get_policy_assets(
            collection_id,
            discriminator=discriminator,
            api_key=self.gomaestroorg_api_key,
            preprod=self.preprod,
        )

        for asset in collection_assets:
            asset_name = asset.asset_name.lower()

            if not asset_name:  # skip royalty token
                continue

            asset_id = f"{collection_id}{asset_name}"
            cip25_metadata = asset.asset_standards.cip25_metadata
            cip68_metadata = asset.asset_standards.cip68_metadata

            metadata = cip68_metadata or cip25_metadata

            if not metadata:
                continue

            yield AssetDTO(
                collection_id=collection_id,
                asset_id=asset_id,
                metadata=metadata,
                supply=asset.total_supply,
            )

    def get_collection_lock_date(self, collection_id: str, *args, **kwargs) -> datetime:
        slot = gomaestroorg.get_policy_lock_slot(
            collection_id,
            api_key=self.gomaestroorg_api_key,
            preprod=self.preprod,
        )

        if slot is None:
            return None

        epoch = SHELLY_EPOCH + (slot - SHELLY_SLOT)
        return datetime.utcfromtimestamp(epoch).replace(tzinfo=pytz.UTC)

    def get_collection_floor(self, collection_id: str, discriminator: str = None, *args, **kwargs) -> FloorDTO:
        self.check_collection_id(collection_id)

        collection_listings = self.get_collection_listings(
            collection_id,
            discriminator=discriminator,
        )

        floor = None
        count = 0

        for listing in collection_listings:
            count += 1

            if floor is None:
                floor = listing
            elif listing.usd < floor.usd:
                floor = listing

        return FloorDTO(
            listing=floor,
            listing_count=count,
        )

    def get_collection_listings(self, collection_id: str, discriminator: str = None, *args, **kwargs) -> Iterable[ListingDTO]:
        self.check_collection_id(collection_id)

        if discriminator:
            discriminator = discriminator.lower()

        collection_listings = jpgstore.get_policy_listings(collection_id)

        for listing in collection_listings:
            asset_id = listing.asset_id
            policy_id, asset_name, _ = utils.split_asset_id(asset_id)

            # required for multi-book policies (e.g. monsters, greek classics)
            if discriminator:
                if not asset_name.startswith(discriminator):
                    continue

            asset_ids = []
            asset_names = []

            if listing.listing_type == "BUNDLE":
                for bundled_asset in listing.bundled_assets:
                    asset_ids.append(bundled_asset.asset_id)
                    asset_names.append(bundled_asset.display_name)
            else:
                asset_ids.append(listing.asset_id)
                asset_names.append(listing.display_name)

            if listing.confirmed_at:
                listed_at = datetime.fromisoformat(listing.confirmed_at.replace("Z", "+00:00"))
            else:
                listed_at = datetime.now(tz=pytz.utc)

            yield ListingDTO(
                identifier=listing.tx_hash,
                collection_id=policy_id,
                asset_ids=asset_ids,
                asset_names=asset_names,
                listing_id=listing.listing_id,
                marketplace=JPG_STORE,
                price=listing.price_lovelace // 10**6,
                currency=self.currency,
                listed_at=listed_at,
                listed_by=None,
                tx_hash=listing.tx_hash,
                marketplace_url=listing.url,
            )

    def get_collection_ranks(self, collection_id: str, *args, **kwargs) -> Iterable[RankDTO]:
        self.check_collection_id(collection_id)

        if collection_id not in CNFT_RANKS:
            return

        for asset_name, rank in CNFT_RANKS[collection_id].items():
            number = int("".join((c for c in asset_name if c.isdigit())))

            yield RankDTO(
                collection_id=collection_id,
                number=number,
                asset_id=None,
                rank=int(rank),
            )

    def get_collection_sales(self, collection_id: str, discriminator: str = None, *args, **kwargs) -> Iterable[SaleDTO]:
        self.check_collection_id(collection_id)

        if discriminator:
            discriminator = discriminator.lower()

        collection_sales = jpgstore.get_collection_sales(collection_id)

        for sale in collection_sales:
            tx_hash = sale.tx_hash

            asset_id = sale.asset_id
            policy_id, asset_name, encoded_asset_name = utils.split_asset_id(asset_id)

            # required for multi-book policies (e.g. monsters, greek classics)
            if discriminator:
                if not asset_name.startswith(discriminator):
                    continue

            bulk_size = sale.bulk_size

            if sale.action == "ACCEPT_OFFER":
                buyer = sale.seller_address
                seller = sale.signer_address
                sale_type = SaleType.OFFER
            elif sale.action == "ACCEPT_COLLECTION_OFFER":
                buyer = sale.signer_address
                seller = sale.seller_address
                sale_type = SaleType.COLLECTION_OFFER
            elif sale.action == "BUY":
                buyer = sale.signer_address
                seller = sale.seller_address
                sale_type = SaleType.PURCHASE
            else:
                continue

            asset_ids = []
            asset_names = []

            if sale.listing_from_tx_history.bundled_assets:
                for bundled_asset in sale.listing_from_tx_history.bundled_assets:
                    asset_ids.append(bundled_asset.asset_id)
                    asset_names.append(bundled_asset.display_name)
            else:
                asset_ids.append(sale.asset_id)
                asset_names.append(sale.display_name)

            if sale.confirmed_at:
                confirmed_at = datetime.fromisoformat(sale.confirmed_at.replace("Z", "+00:00"))
            else:
                confirmed_at = datetime.now(tz=pytz.utc)

            yield SaleDTO(
                identifier=tx_hash,
                collection_id=policy_id,
                asset_ids=asset_ids,
                asset_names=asset_names,
                tx_hash=tx_hash,
                marketplace=JPG_STORE,
                price=sale.amount_lovelace // 10**6,
                currency=self.currency,
                confirmed_at=confirmed_at,
                type=sale_type,
                bulk_size=bulk_size,
                sold_by=seller,
                bought_by=buyer,
                marketplace_url=sale.url,
                explorer_url=f"https://cardanoscan.io/transaction/{tx_hash}",
            )

    def get_collection_supply(self, collection_id: str, discriminator: str = None, *args, **kwargs) -> int:
        self.check_collection_id(collection_id)

        if discriminator:
            return gomaestroorg.get_policy_asset_count(
                collection_id,
                discriminator=discriminator,
                api_key=self.gomaestroorg_api_key,
                preprod=self.preprod,
            )

        return gomaestroorg.get_policy_supply(
            collection_id,
            api_key=self.gomaestroorg_api_key,
            preprod=self.preprod,
        )

    def get_collection_holders(self, collection_id: str, discriminator: str = None, max_threads: int = 3, *args, **kwargs) -> Iterable[HoldingDTO]:
        self.check_collection_id(collection_id)

        collection_owners = gomaestroorg.get_policy_holders(
            collection_id,
            api_key=self.gomaestroorg_api_key,
            preprod=self.preprod,
        )

        for owner in collection_owners:
            stake_address = owner.account

            for asset in owner.assets:
                encoded_asset_name = asset.name.lower()
                asset_id = f"{collection_id}{encoded_asset_name}"
                amount = asset.amount

                # required for multi-book policies (e.g. monsters, greek classics)
                if discriminator:
                    if not encoded_asset_name.startswith(discriminator.lower()):
                        continue

                yield HoldingDTO(
                    collection_id=collection_id,
                    asset_id=asset_id,
                    address=stake_address,
                    amount=amount,
                )

    # others
    def get_otp(self) -> float:
        return float(f"1.{generate_otp()}")

    def verify_otp(self, account: str, otp: float) -> TransactionDTO:
        return super().verify_otp(account.lower(), otp)

    # tokens
    def get_token_exchange(self, collection_id: str, asset_id: str) -> Optional[float]:
        self.check_asset_id(asset_id)

        if collection_id is not None:
            self.check_collection_id(collection_id)

        return dexhunterio.get_asset_average_price(
            asset_id,
            partner_code=self.dexhunterio_partner_code,
        )

    # sanity
    def sanity_check(self) -> bool:
        if self.preprod:
            collection_id = "cd91ae78fc25a1af2091893e59363189cc426d02aaaaf5312d810fc6"
            asset_id = "cd91ae78fc25a1af2091893e59363189cc426d02aaaaf5312d810fc6416c696365496e576f6e6465726c616e64417564696f626f6f6b303335"
            asset_name, asset_number = "Alice in Wonderland", 35
        else:
            collection_id = "9cb921b32bfe214a739ed824f3f2da4e16c535a5448253d2951cc732"
            asset_id = "9cb921b32bfe214a739ed824f3f2da4e16c535a5448253d2951cc732416c696365496e576f6e6465726c616e64303335"
            asset_name, asset_number = "Alice's Adventures in Wonderland", 35

        self.validate_sanity_check(collection_id, asset_id, asset_name, asset_number)

    def api_keys(self) -> List[str]:
        return [
            "m:{gomaestroorg}".format(
                gomaestroorg=self.gomaestroorg_api_key[-3:] if self.gomaestroorg_api_key else "none",
            ),
            "dh:{dexhunterio}".format(
                dexhunterio=self.dexhunterio_partner_code[-3:] if self.dexhunterio_partner_code else "none",
            ),
        ]
