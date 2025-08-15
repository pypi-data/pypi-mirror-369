from typing import Iterable, Tuple

from fetchfox.apis.cardano import gomaestroorg


class CardanoPool:
    def __init__(self, id: str, name: str, fingerprint: str, gomaestroorg_api_key: str = None):
        self.id = id
        self.name = name
        self.fingerprint = fingerprint
        self.gomaestroorg_api_key = gomaestroorg_api_key

    @property
    def delegated_amount(self) -> float:
        info = gomaestroorg.get_pool_information(
            self.fingerprint,
            api_key=self.gomaestroorg_api_key,
        )

        return info["live_stake"] / 10**6

    @property
    def delegator_count(self) -> int:
        info = gomaestroorg.get_pool_information(
            self.fingerprint,
            api_key=self.gomaestroorg_api_key,
        )

        return info["live_delegators"]

    @property
    def saturation(self) -> float:
        info = gomaestroorg.get_pool_information(
            self.fingerprint,
            api_key=self.gomaestroorg_api_key,
        )

        return float(info["live_saturation"])

    @property
    def delegators(self) -> Iterable[Tuple[str, float]]:
        delegators = gomaestroorg.get_pool_delegators(
            self.fingerprint,
            api_key=self.gomaestroorg_api_key,
        )

        for delegator in delegators:
            yield delegator.stake_address, delegator.amount

    @property
    def url(self) -> str:
        return f"https://pool.pm/{self.id}"

    @property
    def __repr__(self):
        return f"{self.name} ({self.id})"
