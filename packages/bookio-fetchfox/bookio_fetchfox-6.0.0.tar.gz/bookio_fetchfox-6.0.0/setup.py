# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fetchfox',
 'fetchfox.apis',
 'fetchfox.apis.algorand',
 'fetchfox.apis.algorand.algonodecloud',
 'fetchfox.apis.algorand.nfdomains',
 'fetchfox.apis.algorand.randswapcom',
 'fetchfox.apis.cardano',
 'fetchfox.apis.cardano.dexhunterio',
 'fetchfox.apis.cardano.gomaestroorg',
 'fetchfox.apis.cardano.jpgstore',
 'fetchfox.apis.coingeckocom',
 'fetchfox.apis.evm',
 'fetchfox.apis.evm.ensideascom',
 'fetchfox.apis.evm.moralisio',
 'fetchfox.apis.evm.openseaio',
 'fetchfox.blockchains',
 'fetchfox.blockchains.algorand',
 'fetchfox.blockchains.cardano',
 'fetchfox.blockchains.coinbase',
 'fetchfox.blockchains.ethereum',
 'fetchfox.blockchains.evm',
 'fetchfox.blockchains.polygon',
 'fetchfox.constants',
 'fetchfox.constants.algorand',
 'fetchfox.constants.cardano',
 'fetchfox.constants.cardano.pools',
 'fetchfox.constants.cardano.tokens',
 'fetchfox.constants.coinbase',
 'fetchfox.constants.ethereum',
 'fetchfox.constants.evm',
 'fetchfox.constants.polygon',
 'fetchfox.dtos',
 'fetchfox.helpers',
 'fetchfox.pools',
 'fetchfox.tokens']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.12.11,<4.0.0',
 'asyncio>=3.4.3,<4.0.0',
 'backoff>=2.2.1,<3.0.0',
 'cachetools>=6.0.0,<7.0.0',
 'certifi>=2025.4.26,<2026.0.0',
 'pydantic>=2.11.5,<3.0.0',
 'pytz>=2025.2,<2026.0']

setup_kwargs = {
    'name': 'bookio-fetchfox',
    'version': '6.0.0',
    'description': 'Collection of API services to fetch information from several blockchains.',
    'long_description': '# book.io / fetchfox\n\n> Collection of API services to fetch information from several blockchains.\n\n![algorand](https://s2.coinmarketcap.com/static/img/coins/64x64/4030.png)\n![cardano](https://s2.coinmarketcap.com/static/img/coins/64x64/2010.png)\n![coinbase](https://s2.coinmarketcap.com/static/img/coins/64x64/27716.png)\n![ethereum](https://s2.coinmarketcap.com/static/img/coins/64x64/1027.png)\n![polygon](https://s2.coinmarketcap.com/static/img/coins/64x64/3890.png)\n\n\n## Supported Blockchains\n\n### Algorand\n\n```python\nimport os\nfrom fetchfox.blockchains import Algorand\n\nalgorand = Algorand()\n\n# Brave New World\ncreator_address = "6WII6ES4H6UW7G7T7RJX63CUNPKJEPEGQ3PTYVVU3JHJ652W34GCJV5OVY"\n\nfor asset in algorand.get_collection_assets(collection_id=creator_address):\n    print(asset)\n```\n\n\n### Cardano\n\n```python\nimport os\nfrom fetchfox.blockchains import Cardano\n\ngomaestroorg_api_key = os.getenv("GOMAESTROORG_API_KEY")\n\ncardano = Cardano(\n    gomaestroorg_api_key=gomaestroorg_api_key,\n)\n\n# Gutenberg Bible\npolicy_id = "477cec772adb1466b301fb8161f505aa66ed1ee8d69d3e7984256a43"\n\nfor asset in cardano.get_collection_assets(collection_id=policy_id):\n    print(asset)\n```\n\n#### API Keys\n\n* [**gomaestro.org**](https://www.gomaestro.org/pricing)\n\n\n### EVM (Coinbase, Ethereum and Polygon)\n\n```python\nimport os\nfrom fetchfox.blockchains import Coinbase, Ethereum, Polygon\n\nmoralisio_api_key = os.getenv("MORALIS_API_KEY")\nopenseaio_api_key = os.getenv("OPENSEA_API_KEY")\n\n\n# Coinbase\ncoinbase = Coinbase(\n    moralisio_api_key=moralisio_api_key,\n    openseaio_api_key=openseaio_api_key,\n)\n\n# Artificial Intelligence for Dummies\ncontract_address = "0x8c1f34bcb76449cebf042cfe8293cd8265ae6802"\n\nfor asset in coinbase.get_collection_assets(collection_id=contract_address):\n    print(asset)\n\n\n# Ethereum\nethereum = Ethereum(\n    moralisio_api_key=moralisio_api_key,\n    openseaio_api_key=openseaio_api_key,\n)\n\n# Alice in Wonderland\ncontract_address = "0x919da7fef646226f88f70305201de392ff365059"\n\nfor asset in ethereum.get_collection_assets(collection_id=contract_address):\n    print(asset)\n\n\n# Polygon\npolygon = Polygon(\n    moralisio_api_key=moralisio_api_key,\n    openseaio_api_key=openseaio_api_key,\n)\n\n# Art of War\ncontract_address = "0xb56010e0500e4f163758881603b8083996ae47ec"\n\nfor asset in polygon.get_collection_assets(collection_id=contract_address):\n    print(asset)\n```\n\n#### API Keys\n\n* [**moralis.io**](https://moralis.io/pricing)\n* [**opensea.io**](https://docs.opensea.io/reference/api-keys)\n\n---\n\n![fetch, the fox](https://i.imgur.com/fm6mqzS.png)\n',
    'author': 'Fede',
    'author_email': 'fede@book.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/book-io/fetchfox',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
