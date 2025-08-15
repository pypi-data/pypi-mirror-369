import logging
from functools import lru_cache
from typing import Optional

from fetchfox.checks import check_str
from .common import get

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def resolve(nf_domain: str) -> Optional[str]:
    check_str(nf_domain, "nfddomains.nf_domain")

    response, status_code = get(
        service=f"nfd/{nf_domain}",
    )

    if not response:
        return None

    address = response["owner"]
    logger.info("resolved %s to %s", nf_domain, address)

    return address


@lru_cache(maxsize=None)
def get_domain(address: str) -> Optional[str]:
    check_str(address, "nfddomains.address")
    address = address.strip().upper()

    response, status_code = get(
        service=f"nfd/v2/address",
        params={
            "address": address,
        },
    )

    if status_code == 404:
        return None

    nf_domains = sorted(
        set(map(lambda nfd: nfd["name"], response[address])),
        key=len,
    )

    if not nf_domains:
        return None

    nf_domain = nf_domains[0]
    logger.info("resolved %s to %s", address, nf_domain)

    return nf_domain
