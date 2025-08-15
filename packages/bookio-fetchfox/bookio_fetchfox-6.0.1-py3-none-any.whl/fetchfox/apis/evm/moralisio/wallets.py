from typing import Iterable

from fetchfox.checks import check_str
from .common import get
from .schemas import WalletTransactionsSchema


def get_transactions(address: str, blockchain: str, api_key: str = None, preprod: bool = False) -> Iterable[WalletTransactionsSchema]:
    check_str(address, "moralisio.address")
    address = address.strip().lower()

    cursor = ""

    while True:
        response, status_code = get(
            service=f"wallets/{address}/history",
            params={
                "cursor": cursor,
                "order": "DESC",
            },
            blockchain=blockchain,
            api_key=api_key,
            preprod=preprod,
        )

        if not response:
            break

        for tx in response.get("result", []):
            if tx.get("possible_spam"):
                continue

            yield WalletTransactionsSchema.model_validate(tx)

        if not response.get("cursor"):
            break

        cursor = response["cursor"]
