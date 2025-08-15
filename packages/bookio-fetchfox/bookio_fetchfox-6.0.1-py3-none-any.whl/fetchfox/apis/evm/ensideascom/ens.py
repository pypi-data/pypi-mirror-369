import logging
from functools import lru_cache

from fetchfox.checks import check_str
from .common import get

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def get_domain(address: str) -> str:
    check_str(address, "ensideascom.address")

    response, status_code = get(
        service=f"ens/resolve/{address}",
    )

    ens_domain = response.get("name")

    if not ens_domain:
        return None

    logger.info("resolved %s to %s", address, ens_domain)

    return ens_domain


@lru_cache(maxsize=None)
def resolve(ens_domain: str) -> str:
    check_str(ens_domain, "ensideascom.ens_domain")

    response, status_code = get(
        service=f"ens/resolve/{ens_domain}",
    )

    address = response.get("address")

    if not address:
        return None

    logger.info("resolved %s to %s", ens_domain, address)

    return address
