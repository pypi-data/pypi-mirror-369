from typing import Iterable

from fetchfox.checks import check_str
from .common import get
from .schemas import CollectionSale


def get_sales(policy_id: str) -> Iterable[CollectionSale]:
    check_str(policy_id, "jpgstore.policy_id")
    policy_id = policy_id.strip().lower()

    txs = set()

    last_date = ""

    while True:
        response, status_code = get(
            service=f"collection/{policy_id}/v2/transactions",
            params={
                "lastDate": last_date,
                "count": 50,
            },
            headers={
                "x-jpgstore-csrf-protection": "1",
            },
        )

        transactions = response.get("transactions")

        if not transactions:  # pragma: no cover
            break

        for transaction in transactions:
            sale = CollectionSale.model_validate(transaction)

            if sale.tx_hash in txs:
                continue

            txs.add(sale.tx_hash)
            last_date = sale.created_at

            yield sale
