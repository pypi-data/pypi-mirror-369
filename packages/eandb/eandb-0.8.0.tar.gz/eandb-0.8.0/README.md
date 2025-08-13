# EAN-DB Python client

This is a Python client for EAN-DB API.

[EAN-DB](https://ean-db.com) is an online API for product info lookups by EAN / UPC / ISBN.
Product info includes titles in various languages, categories, manufacturer, images and additional metadata.

For more information, please see [API docs](https://ean-db.com/docs) and [Database stats](https://ean-db.com/stats).

## Installation

```commandline
pip install eandb
```

## Usage

### Asynchronous client

```pycon
>>> from eandb.clients.v2 import EandbV2AsyncClient

>>> eandb_client = EandbV2AsyncClient(jwt='YOUR_JWT_GOES_HERE')
>>> response = await eandb_client.get_product('0016065024615')
```

### Synchronous client

```pycon
>>> from eandb.clients.v2 import EandbV2SyncClient

>>> eandb_client = EandbV2SyncClient(jwt='YOUR_JWT_GOES_HERE')
>>> response = eandb_client.get_product('0016065024615')
>>> response

ProductResponse(
    balance=100, error=None, 
    product=Product(
        barcode='0016065024615', 
        titles={'en': 'Pretty Tied Up'}, 
        categories=[
            Category(id='855', titles={'en': 'Music & Sound Recordings', ...})
        ],
        manufacturer=Manufacturer(id=None, titles={'de': 'Geffen'}, wikidataId=None),
        relatedBrands=[],
        images=[Image(url='...')], 
        metadata=Metadata(
            generic=Generic(
                contributors=[Contributor(names={'en': "Guns N' Roses"}, type='artist')]
            )
        )
    )
)
```
