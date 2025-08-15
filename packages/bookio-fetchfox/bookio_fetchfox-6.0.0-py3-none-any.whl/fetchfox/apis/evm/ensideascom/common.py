import logging
import os
from typing import Tuple

from fetchfox import rest

BASE_URL_DEFAULT = "https://api.ensideas.com"
BASE_URL = os.getenv("ENSIDEASCOM_BASE_URL") or BASE_URL_DEFAULT

logger = logging.getLogger(__name__)


def get(service: str, params: dict = None) -> Tuple[dict, int]:
    return rest.get(
        url=f"{BASE_URL}/{service}",
        params=params,
    )
