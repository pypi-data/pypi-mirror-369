class HoldingDTO:
    def __init__(self, collection_id: str, asset_id: str, address: str, amount: float):
        self.collection_id: str = collection_id
        self.asset_id: str = asset_id
        self.address: str = address
        self.amount: float = amount

    def __repr__(self) -> str:
        if not self.collection_id:
            return f"{self.address}: {self.asset_id} x {self.amount}"

        return f"{self.address}: {self.collection_id}/{self.asset_id} x {self.amount}"
