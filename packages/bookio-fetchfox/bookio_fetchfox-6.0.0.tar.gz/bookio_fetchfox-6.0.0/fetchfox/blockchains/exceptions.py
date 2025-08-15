class InvalidCollectionIdException(ValueError):
    def __init__(self, string: str):
        super().__init__(string)


class InvalidAssetIdException(ValueError):
    def __init__(self, string: str):
        super().__init__(string)


class InvalidWalletException(ValueError):
    def __init__(self, string: str):
        super().__init__(string)


class UnavailableMetadataException(Exception):
    def __init__(self, string: str):
        super().__init__(string)
