from .common import get
from .schemas import TransactionSchema


def get_transaction(tx_hash: str, api_key: str = None, preprod: bool = False) -> TransactionSchema:
    response, status_code = get(
        service=f"transactions/{tx_hash}",
        api_key=api_key,
        preprod=preprod,
        check="data",
    )

    return TransactionSchema.model_validate(response["data"])
