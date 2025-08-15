from ..exceptions import (
    InvalidCollectionIdException,
    InvalidAssetIdException,
    InvalidWalletException,
)


class InvalidAlgorandCollectionIdException(InvalidCollectionIdException):
    def __init__(self, string: str):
        super().__init__(f"'{string}' is not a valid algorand creator address.")


class InvalidAlgorandAssetIdException(InvalidAssetIdException):
    def __init__(self, string: str):
        super().__init__(f"'{string}' is not a valid algorand asset id.")


class InvalidAlgorandAccountException(InvalidWalletException):
    def __init__(self, string: str):
        super().__init__(f"'{string}' is not a valid algorand address or non-fungible domain.")
