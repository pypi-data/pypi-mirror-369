from typing import Iterable

from fetchfox.checks import check_str
from .common import get
from .schemas import PolicyListing


def get_listings(policy_id: str) -> Iterable[PolicyListing]:
    check_str(policy_id, "jpgstore.policy_id")
    policy_id = policy_id.strip().lower()

    cursor = ""

    while True:
        params = {}

        if cursor:
            params["cursor"] = cursor

        response, status_code = get(
            service=f"policy/{policy_id}/listings",
            params=params,
        )

        cursor = response.get("nextPageCursor")

        if not cursor:  # pragma: no cover
            break

        yield from map(
            PolicyListing.model_validate,
            response["listings"],
        )
