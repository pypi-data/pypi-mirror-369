# channel3_sdk/client.py
import os
from typing import Any, Dict, List, Optional, Union

from ._gen.fast_api_client.api.channel3_api.get_brand_detail_v0_brands_brand_id_get import (
    asyncio_detailed as get_brand_asyncio_detailed,
)
from ._gen.fast_api_client.api.channel3_api.get_brand_detail_v0_brands_brand_id_get import (
    sync_detailed as get_brand_sync_detailed,
)
from ._gen.fast_api_client.api.channel3_api.get_brands_v0_brands_get import (
    asyncio_detailed as get_brands_asyncio_detailed,
)
from ._gen.fast_api_client.api.channel3_api.get_brands_v0_brands_get import (
    sync_detailed as get_brands_sync_detailed,
)
from ._gen.fast_api_client.api.channel3_api.get_product_detail_v0_products_product_id_get import (
    asyncio_detailed as get_product_asyncio_detailed,
)
from ._gen.fast_api_client.api.channel3_api.get_product_detail_v0_products_product_id_get import (
    sync_detailed as get_product_sync_detailed,
)
from ._gen.fast_api_client.api.channel3_api.search_v0_search_post import (
    asyncio_detailed as search_asyncio_detailed,
)
from ._gen.fast_api_client.api.channel3_api.search_v0_search_post import (
    sync_detailed as search_sync_detailed,
)

# Generated client imports
from ._gen.fast_api_client.client import AuthenticatedClient
from ._gen.fast_api_client.models.error_response import (
    ErrorResponse as GenErrorResponse,
)
from ._gen.fast_api_client.models.paginated_response_brand import (
    PaginatedResponseBrand as GenPaginatedResponseBrand,
)
from ._gen.fast_api_client.models.product import Product as GenProduct
from ._gen.fast_api_client.models.product_detail import (
    ProductDetail as GenProductDetail,
)
from ._gen.fast_api_client.models.search_config import (
    SearchConfig as GenSearchConfig,
)
from ._gen.fast_api_client.models.search_filter_price import (
    SearchFilterPrice as GenSearchFilterPrice,
)
from ._gen.fast_api_client.models.search_filters import (
    SearchFilters as GenSearchFilters,
)
from ._gen.fast_api_client.models.search_request import (
    SearchRequest as GenSearchRequest,
)
from ._gen.fast_api_client.types import UNSET
from ._gen.fast_api_client.types import Response as GenResponse
from .exceptions import (
    Channel3AuthenticationError,
    Channel3ConnectionError,
    Channel3Error,
    Channel3NotFoundError,
    Channel3ServerError,
    Channel3ValidationError,
)


def _strip_v0_suffix(base_url: str) -> str:
    if base_url.endswith("/v0"):
        return base_url[:-3]
    return base_url


def _convert_filters_to_generated(
    filters: Optional[GenSearchFilters | Dict[str, Any]],
) -> Optional[GenSearchFilters]:
    if filters is None:
        return None
    if isinstance(filters, GenSearchFilters):
        return filters
    # dict → generated model
    price = None
    price_dict = filters.get("price") if isinstance(filters, dict) else None
    if isinstance(price_dict, dict):
        price = GenSearchFilterPrice(
            min_price=price_dict.get("min_price"),
            max_price=price_dict.get("max_price"),
        )
    return GenSearchFilters(
        brand_ids=filters.get("brand_ids"),  # type: ignore[arg-type]
        gender=filters.get("gender"),  # type: ignore[arg-type]
        price=price,
        availability=filters.get("availability"),  # type: ignore[arg-type]
    )


def _convert_config_to_generated(
    config: Optional[Union[GenSearchConfig, Dict[str, Any]]],
) -> Optional[GenSearchConfig]:
    if config is None:
        return None
    if isinstance(config, GenSearchConfig):
        return config
    # dict → generated model
    return GenSearchConfig(
        enrich_query=config.get("enrich_query", True),
        semantic_search=config.get("semantic_search", True),
    )


def _raise_for_status(url: str, response: GenResponse[Any]) -> None:
    status_code = int(response.status_code)
    data: Dict[str, Any] = {}
    if response.parsed is not None and isinstance(response.parsed, GenErrorResponse):
        detail = response.parsed.detail
        if isinstance(detail, dict):
            data = detail
        else:
            data = {"detail": detail}
    error_message = data.get("detail") if isinstance(data.get("detail"), str) else None
    if status_code == 200:
        return
    if status_code == 401:
        raise Channel3AuthenticationError(
            "Invalid or missing API key", status_code=status_code, response_data=data
        )
    if status_code == 404:
        raise Channel3NotFoundError(
            error_message or "Resource not found",
            status_code=status_code,
            response_data=data,
        )
    if status_code == 422:
        raise Channel3ValidationError(
            f"Validation error: {error_message or 'Unprocessable Entity'}",
            status_code=status_code,
            response_data=data,
        )
    if status_code == 500:
        raise Channel3ServerError(
            "Internal server error", status_code=status_code, response_data=data
        )
    raise Channel3Error(
        f"Request to {url} failed: {error_message or f'Status {status_code}'}",
        status_code=status_code,
        response_data=data,
    )


class BaseChannel3Client:
    """Base client with common functionality."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("CHANNEL3_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No API key provided. Set CHANNEL3_API_KEY environment variable or pass api_key parameter."
            )

        self.base_url = base_url or "https://api.trychannel3.com/v0"
        self.headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}

    def _build_generated_client(self) -> AuthenticatedClient:
        gen_base_url = _strip_v0_suffix(self.base_url)
        client = AuthenticatedClient(
            base_url=gen_base_url,
            token=self.api_key,
            prefix="",
            auth_header_name="x-api-key",
        )
        client = client.with_headers({"Content-Type": "application/json"})
        return client


class Channel3Client(BaseChannel3Client):
    """Synchronous Channel3 API client (returns generated models)."""

    def search(
        self,
        query: Optional[str] = None,
        image_url: Optional[str] = None,
        base64_image: Optional[str] = None,
        filters: Optional[Union[GenSearchFilters, Dict[str, Any]]] = None,
        limit: int = 20,
        config: Optional[Union[GenSearchConfig, Dict[str, Any]]] = None,
        context: Optional[str] = None,
    ) -> List[GenProduct]:
        gen_client = self._build_generated_client()
        request_body = GenSearchRequest(
            query=query,
            image_url=image_url,
            base64_image=base64_image,
            filters=_convert_filters_to_generated(filters)
            if filters is not None
            else UNSET,  # type: ignore[arg-type]
            limit=limit,
            config=_convert_config_to_generated(config)
            if config is not None
            else UNSET,  # type: ignore[arg-type]
            context=context,
        )

        try:
            response = search_sync_detailed(client=gen_client, body=request_body)
            self._raise_and_validate_search(response)
            return response.parsed  # type: ignore[return-value]
        except Exception as e:
            if isinstance(e, Channel3Error):
                raise
            raise Channel3ConnectionError(f"Request failed: {str(e)}")

    def _raise_and_validate_search(
        self, response: GenResponse[Union[GenErrorResponse, List[Any]]]
    ) -> None:
        url = f"{_strip_v0_suffix(self.base_url)}/v0/search"
        _raise_for_status(url, response)
        if not isinstance(response.parsed, list):
            raise Channel3Error("Invalid response format: expected list of products")

    def get_product(self, product_id: str) -> GenProductDetail:
        if not product_id or not product_id.strip():
            raise ValueError("product_id cannot be empty")

        gen_client = self._build_generated_client()
        try:
            response = get_product_sync_detailed(
                product_id=product_id, client=gen_client
            )
            url = f"{_strip_v0_suffix(self.base_url)}/v0/products/{product_id}"
            _raise_for_status(url, response)
            return response.parsed  # type: ignore[return-value]
        except Exception as e:
            if isinstance(e, Channel3Error):
                raise
            raise Channel3ConnectionError(f"Request failed: {str(e)}")

    def get_brands(
        self,
        query: Optional[str] = None,
        page: int = 1,
        size: int = 100,
    ) -> GenPaginatedResponseBrand:
        gen_client = self._build_generated_client()
        try:
            response = get_brands_sync_detailed(
                client=gen_client, query=query, page=page, size=size
            )
            url = f"{_strip_v0_suffix(self.base_url)}/v0/brands"
            _raise_for_status(url, response)
            return response.parsed  # type: ignore[return-value]
        except Exception as e:
            if isinstance(e, Channel3Error):
                raise
            raise Channel3ConnectionError(f"Request failed: {str(e)}")

    def get_brand(self, brand_id: str) -> Any:
        if not brand_id or not brand_id.strip():
            raise ValueError("brand_id cannot be empty")

        gen_client = self._build_generated_client()
        try:
            response = get_brand_sync_detailed(brand_id=brand_id, client=gen_client)
            url = f"{_strip_v0_suffix(self.base_url)}/v0/brands/{brand_id}"
            _raise_for_status(url, response)
            return response.parsed
        except Exception as e:
            if isinstance(e, Channel3Error):
                raise
            raise Channel3ConnectionError(f"Request failed: {str(e)}")


class AsyncChannel3Client(BaseChannel3Client):
    """Asynchronous Channel3 API client (returns generated models)."""

    async def search(
        self,
        query: Optional[str] = None,
        image_url: Optional[str] = None,
        base64_image: Optional[str] = None,
        filters: Optional[Union[GenSearchFilters, Dict[str, Any]]] = None,
        limit: int = 20,
        config: Optional[Union[GenSearchConfig, Dict[str, Any]]] = None,
        context: Optional[str] = None,
    ) -> List[GenProduct]:
        gen_client = self._build_generated_client()
        request_body = GenSearchRequest(
            query=query,
            image_url=image_url,
            base64_image=base64_image,
            filters=_convert_filters_to_generated(filters)
            if filters is not None
            else UNSET,  # type: ignore[arg-type]
            limit=limit,
            config=_convert_config_to_generated(config)
            if config is not None
            else UNSET,  # type: ignore[arg-type]
            context=context,
        )

        try:
            response = await search_asyncio_detailed(
                client=gen_client, body=request_body
            )
            url = f"{_strip_v0_suffix(self.base_url)}/v0/search"
            _raise_for_status(url, response)
            return response.parsed  # type: ignore[return-value]
        except Exception as e:
            if isinstance(e, Channel3Error):
                raise
            raise Channel3ConnectionError(f"Request failed: {str(e)}")

    async def get_product(self, product_id: str) -> GenProductDetail:
        if not product_id or not product_id.strip():
            raise ValueError("product_id cannot be empty")

        gen_client = self._build_generated_client()
        try:
            response = await get_product_asyncio_detailed(
                product_id=product_id, client=gen_client
            )
            url = f"{_strip_v0_suffix(self.base_url)}/v0/products/{product_id}"
            _raise_for_status(url, response)
            return response.parsed  # type: ignore[return-value]
        except Exception as e:
            if isinstance(e, Channel3Error):
                raise
            raise Channel3ConnectionError(f"Request failed: {str(e)}")

    async def get_brands(
        self,
        query: Optional[str] = None,
        page: int = 1,
        size: int = 100,
    ) -> GenPaginatedResponseBrand:
        gen_client = self._build_generated_client()
        try:
            response = await get_brands_asyncio_detailed(
                client=gen_client, query=query, page=page, size=size
            )
            url = f"{_strip_v0_suffix(self.base_url)}/v0/brands"
            _raise_for_status(url, response)
            return response.parsed  # type: ignore[return-value]
        except Exception as e:
            if isinstance(e, Channel3Error):
                raise
            raise Channel3ConnectionError(f"Request failed: {str(e)}")

    async def get_brand(self, brand_id: str) -> Any:
        if not brand_id or not brand_id.strip():
            raise ValueError("brand_id cannot be empty")

        gen_client = self._build_generated_client()
        try:
            response = await get_brand_asyncio_detailed(
                brand_id=brand_id, client=gen_client
            )
            url = f"{_strip_v0_suffix(self.base_url)}/v0/brands/{brand_id}"
            _raise_for_status(url, response)
            return response.parsed  # type: ignore[return-value]
        except Exception as e:
            if isinstance(e, Channel3Error):
                raise
            raise Channel3ConnectionError(f"Request failed: {str(e)}")
