# book.io / fetchfox

> Collection of API services to fetch information from several blockchains.

![algorand](https://s2.coinmarketcap.com/static/img/coins/64x64/4030.png)
![cardano](https://s2.coinmarketcap.com/static/img/coins/64x64/2010.png)
![coinbase](https://s2.coinmarketcap.com/static/img/coins/64x64/27716.png)
![ethereum](https://s2.coinmarketcap.com/static/img/coins/64x64/1027.png)
![polygon](https://s2.coinmarketcap.com/static/img/coins/64x64/3890.png)


## Supported Blockchains

### Algorand

```python
import os
from fetchfox.blockchains import Algorand

algorand = Algorand()

# Brave New World
creator_address = "6WII6ES4H6UW7G7T7RJX63CUNPKJEPEGQ3PTYVVU3JHJ652W34GCJV5OVY"

for asset in algorand.get_collection_assets(collection_id=creator_address):
    print(asset)
```


### Cardano

```python
import os
from fetchfox.blockchains import Cardano

gomaestroorg_api_key = os.getenv("GOMAESTROORG_API_KEY")

cardano = Cardano(
    gomaestroorg_api_key=gomaestroorg_api_key,
)

# Gutenberg Bible
policy_id = "477cec772adb1466b301fb8161f505aa66ed1ee8d69d3e7984256a43"

for asset in cardano.get_collection_assets(collection_id=policy_id):
    print(asset)
```

#### API Keys

* [**gomaestro.org**](https://www.gomaestro.org/pricing)


### EVM (Coinbase, Ethereum and Polygon)

```python
import os
from fetchfox.blockchains import Coinbase, Ethereum, Polygon

moralisio_api_key = os.getenv("MORALIS_API_KEY")
openseaio_api_key = os.getenv("OPENSEA_API_KEY")


# Coinbase
coinbase = Coinbase(
    moralisio_api_key=moralisio_api_key,
    openseaio_api_key=openseaio_api_key,
)

# Artificial Intelligence for Dummies
contract_address = "0x8c1f34bcb76449cebf042cfe8293cd8265ae6802"

for asset in coinbase.get_collection_assets(collection_id=contract_address):
    print(asset)


# Ethereum
ethereum = Ethereum(
    moralisio_api_key=moralisio_api_key,
    openseaio_api_key=openseaio_api_key,
)

# Alice in Wonderland
contract_address = "0x919da7fef646226f88f70305201de392ff365059"

for asset in ethereum.get_collection_assets(collection_id=contract_address):
    print(asset)


# Polygon
polygon = Polygon(
    moralisio_api_key=moralisio_api_key,
    openseaio_api_key=openseaio_api_key,
)

# Art of War
contract_address = "0xb56010e0500e4f163758881603b8083996ae47ec"

for asset in polygon.get_collection_assets(collection_id=contract_address):
    print(asset)
```

#### API Keys

* [**moralis.io**](https://moralis.io/pricing)
* [**opensea.io**](https://docs.opensea.io/reference/api-keys)

---

![fetch, the fox](https://i.imgur.com/fm6mqzS.png)
