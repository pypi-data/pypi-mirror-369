from typing import Iterable

from fetchfox.checks import check_str
from .common import get
from .schemas import PoolInformationSchema, PoolDelegatorSchema


def get_information(pool_id: str, api_key: str = None, preprod: bool = False) -> PoolInformationSchema:
    check_str(pool_id, "gomaestroorg.pool_id")

    pool_id = pool_id.strip().lower()

    response, status_code = get(
        service=f"pools/{pool_id}/info",
        api_key=api_key,
        preprod=preprod,
    )

    return PoolInformationSchema.model_validate(response["data"])


def get_delegators(pool_id: str, api_key: str = None, preprod: bool = False) -> Iterable[PoolDelegatorSchema]:
    check_str(pool_id, "gomaestroorg.pool_id")

    pool_id = pool_id.strip().lower()

    cursor = None

    while True:
        response, status_code = get(
            service=f"pools/{pool_id}/delegators",
            params={
                "cursor": cursor,
            },
            api_key=api_key,
            preprod=preprod,
            check="data",
        )

        for item in response.get("data", []):
            delegator = PoolDelegatorSchema.model_validate(item)

            if delegator.amount == 0:
                continue

            yield delegator

        cursor = response.get("next_cursor")

        if not cursor:
            break
