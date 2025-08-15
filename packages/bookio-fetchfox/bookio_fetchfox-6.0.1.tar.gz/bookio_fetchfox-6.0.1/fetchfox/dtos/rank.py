class RankDTO:
    def __init__(self, collection_id: str, asset_id: str, number: int, rank: int):
        self.collection_id: str = collection_id
        self.asset_id: str = asset_id
        self.number: int = number
        self.rank: int = rank

    def __repr__(self) -> str:
        return f"{self.collection_id}/{self.asset_id} ({self.number}): #{self.rank}"
