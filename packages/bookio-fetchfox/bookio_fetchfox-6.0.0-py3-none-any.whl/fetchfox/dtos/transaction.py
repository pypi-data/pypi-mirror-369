from typing import List


class TransactionAssetDTO:
    def __init__(self, amount: float, unit: str):
        self.amount: float = amount
        self.unit: str = unit

    def __repr__(self) -> str:
        return f"{self.amount} {self.unit}"


class TransactionInputOutputDTO:
    def __init__(self, address: str, assets: List[TransactionAssetDTO]):
        self.address: str = address
        self.assets: List[TransactionAssetDTO] = assets

    def __repr__(self) -> str:
        string = f"{self.address}: "

        for asset in self.assets:
            string += f"\n - {asset}"

        return string


class TransactionDTO:
    def __init__(
        self,
        blockchain: str,
        address: str,
        tx_hash: str,
        inputs: List[TransactionInputOutputDTO],
        outputs: List[TransactionInputOutputDTO],
        message: str = None,
    ):
        self.blockchain: str = blockchain
        self.address: str = address
        self.tx_hash: str = tx_hash
        self.inputs: List[TransactionInputOutputDTO] = inputs
        self.outputs: List[TransactionInputOutputDTO] = outputs
        self.message: str = message

    def __repr__(self) -> str:
        if not self.message:
            return self.tx_hash

        return f"{self.tx_hash} / {self.message}"
