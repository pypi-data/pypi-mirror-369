from ..exceptions import (
    InvalidCollectionIdException,
    InvalidAssetIdException,
    InvalidWalletException,
)


class InvalidCardanoCollectionIdException(InvalidCollectionIdException):
    def __init__(self, string: str):
        super().__init__(f"'{string}' is not a valid cardano policy id.")


class InvalidCardanoAssetIdException(InvalidAssetIdException):
    def __init__(self, string: str):
        super().__init__(f"'{string}' is not a valid cardano asset id.")


class InvalidCardanoAccountException(InvalidWalletException):
    def __init__(self, string: str):
        super().__init__(f"'{string}' is not a valid cardano stake key, address or ada handle.")
