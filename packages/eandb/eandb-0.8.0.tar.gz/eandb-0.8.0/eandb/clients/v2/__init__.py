import abc
from types import TracebackType
from typing import Optional, Type

import httpx

from eandb.models.v2 import ProductResponse, EandbResponse


class EandbV2AbstractClient(abc.ABC):
    DEFAULT_BASE_URL = 'https://ean-db.com'
    PRODUCT_ENDPOINT = '/api/v2/product/{barcode}'

    def __init__(self, *, jwt: str = ''):
        if not jwt:
            raise ValueError('`jwt` param is empty')

        self.jwt = jwt

    @staticmethod
    def _process_product_response(response: httpx.Response) -> ProductResponse | EandbResponse:
        if response.status_code == httpx.codes.OK:
            return ProductResponse.model_validate(response.json())

        if response.status_code in (httpx.codes.NOT_FOUND, httpx.codes.FORBIDDEN, httpx.codes.BAD_REQUEST):
            return EandbResponse.model_validate(response.json())

        response.raise_for_status()


class EandbV2SyncClient(EandbV2AbstractClient):
    def __init__(self, *, jwt: str = '', **kwargs):
        super().__init__(jwt=jwt)

        default_headers = {'Authorization': f'Bearer {jwt}', 'Accept': 'application/json'}

        self._client = httpx.Client(
            headers=kwargs.get('headers', default_headers),
            base_url=kwargs.get('base_url', self.DEFAULT_BASE_URL),
            **kwargs
        )

    def get_product(self, barcode: str) -> ProductResponse | EandbResponse:
        """
        Returns product info by barcode.
        An exception (`httpx.HTTPStatusError`) is raised in case of any unexpected error (5xx or transport error).

        :param barcode: Barcode (EAN / UPC / ISBN) of a product
        :return: `ProductResponse` object with product info or `EandbResponse` object with error info.
        """
        response = self._client.get(self.PRODUCT_ENDPOINT.format(barcode=barcode))
        return self._process_product_response(response)

    def close(self):
        """
        Closes underlying httpx client.
        """
        self._client.close()

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ):
        self._client.__exit__(exc_type, exc_value, traceback)


class EandbV2AsyncClient(EandbV2AbstractClient):
    def __init__(self, *, jwt: str = '', **kwargs):
        super().__init__(jwt=jwt)

        default_headers = {'Authorization': f'Bearer {jwt}', 'Accept': 'application/json'}

        self._client = httpx.AsyncClient(
            headers=kwargs.get('headers', default_headers),
            base_url=kwargs.get('base_url', self.DEFAULT_BASE_URL),
            **kwargs
        )

    async def get_product(self, barcode: str) -> ProductResponse | EandbResponse:
        """
        Returns product info by barcode.
        An exception (`httpx.HTTPStatusError`) is raised in case of any unexpected error (5xx or transport error).

        :param barcode: Barcode (EAN / UPC / ISBN) of a product
        :return: `ProductResponse` object with product info or `EandbResponse` object with error info.
        """
        response = await self._client.get(self.PRODUCT_ENDPOINT.format(barcode=barcode))
        return self._process_product_response(response)

    async def aclose(self):
        """
        Closes underlying httpx client.
        """
        await self._client.aclose()

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ):
        await self._client.__aexit__(exc_type, exc_value, traceback)
