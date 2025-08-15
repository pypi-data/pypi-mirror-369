from ..exceptions import (
    InvalidCollectionIdException,
    InvalidAssetIdException,
    InvalidWalletException,
)


class InvalidEvmAccountException(InvalidWalletException):
    def __init__(self, string: str, blockchain: str = "evm"):
        super().__init__(f"'{string}' is not a valid {blockchain} address or ens domain.")


class InvalidEvmCollectionIdException(InvalidCollectionIdException):
    def __init__(self, string: str, blockchain: str = "evm"):
        super().__init__(f"'{string}' is not a valid {blockchain} contract address.")


class InvalidEvmAssetIdException(InvalidAssetIdException):
    def __init__(self, string: str, blockchain: str = "evm"):
        super().__init__(f"'{string}' is not a valid {blockchain} asset id.")
