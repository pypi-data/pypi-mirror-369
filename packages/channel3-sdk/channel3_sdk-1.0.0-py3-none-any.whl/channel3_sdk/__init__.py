"""Channel3 SDK for Python - Official SDK for the Channel3 AI Shopping API."""

from ._gen.fast_api_client.models.availability_status import AvailabilityStatus
from ._gen.fast_api_client.models.brand import Brand
from ._gen.fast_api_client.models.paginated_response_brand import (
    PaginatedResponseBrand,
)

# Re-export generated models so the public API returns exactly what the OpenAPI returns
from ._gen.fast_api_client.models.pagination_meta import PaginationMeta
from ._gen.fast_api_client.models.price import Price
from ._gen.fast_api_client.models.product import Product
from ._gen.fast_api_client.models.product_detail import ProductDetail
from ._gen.fast_api_client.models.search_config import SearchConfig
from ._gen.fast_api_client.models.search_filters import SearchFilters
from ._gen.fast_api_client.models.search_request import SearchRequest
from ._gen.fast_api_client.models.variant import Variant
from .client import AsyncChannel3Client, Channel3Client
from .exceptions import (
    Channel3AuthenticationError,
    Channel3ConnectionError,
    Channel3Error,
    Channel3NotFoundError,
    Channel3ServerError,
    Channel3ValidationError,
)

__version__ = "1.0.0"
__all__ = [
    # Clients
    "Channel3Client",
    "AsyncChannel3Client",
    # Models (generated)
    "Product",
    "ProductDetail",
    "SearchFilters",
    "SearchConfig",
    "SearchRequest",
    "Brand",
    "Variant",
    "Price",
    "AvailabilityStatus",
    "PaginatedResponseBrand",
    "PaginationMeta",
    # Exceptions
    "Channel3Error",
    "Channel3AuthenticationError",
    "Channel3ValidationError",
    "Channel3NotFoundError",
    "Channel3ServerError",
    "Channel3ConnectionError",
]
