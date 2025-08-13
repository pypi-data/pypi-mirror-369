from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.paginated_response_brand import PaginatedResponseBrand
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    query: Union[None, Unset, str] = UNSET,
    page: Union[Unset, int] = 1,
    size: Union[Unset, int] = 100,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_query: Union[None, Unset, str]
    if isinstance(query, Unset):
        json_query = UNSET
    else:
        json_query = query
    params["query"] = json_query

    params["page"] = page

    params["size"] = size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v0/brands",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, PaginatedResponseBrand]]:
    if response.status_code == 200:
        response_200 = PaginatedResponseBrand.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())

        return response_401
    if response.status_code == 402:
        response_402 = ErrorResponse.from_dict(response.json())

        return response_402
    if response.status_code == 422:
        response_422 = ErrorResponse.from_dict(response.json())

        return response_422
    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ErrorResponse, PaginatedResponseBrand]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    query: Union[None, Unset, str] = UNSET,
    page: Union[Unset, int] = 1,
    size: Union[Unset, int] = 100,
) -> Response[Union[ErrorResponse, PaginatedResponseBrand]]:
    """Get Brands

     Get all brands that the vendor currently sells.

    Args:
        query (Union[None, Unset, str]):
        page (Union[Unset, int]):  Default: 1.
        size (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, PaginatedResponseBrand]]
    """

    kwargs = _get_kwargs(
        query=query,
        page=page,
        size=size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    query: Union[None, Unset, str] = UNSET,
    page: Union[Unset, int] = 1,
    size: Union[Unset, int] = 100,
) -> Optional[Union[ErrorResponse, PaginatedResponseBrand]]:
    """Get Brands

     Get all brands that the vendor currently sells.

    Args:
        query (Union[None, Unset, str]):
        page (Union[Unset, int]):  Default: 1.
        size (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, PaginatedResponseBrand]
    """

    return sync_detailed(
        client=client,
        query=query,
        page=page,
        size=size,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    query: Union[None, Unset, str] = UNSET,
    page: Union[Unset, int] = 1,
    size: Union[Unset, int] = 100,
) -> Response[Union[ErrorResponse, PaginatedResponseBrand]]:
    """Get Brands

     Get all brands that the vendor currently sells.

    Args:
        query (Union[None, Unset, str]):
        page (Union[Unset, int]):  Default: 1.
        size (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, PaginatedResponseBrand]]
    """

    kwargs = _get_kwargs(
        query=query,
        page=page,
        size=size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    query: Union[None, Unset, str] = UNSET,
    page: Union[Unset, int] = 1,
    size: Union[Unset, int] = 100,
) -> Optional[Union[ErrorResponse, PaginatedResponseBrand]]:
    """Get Brands

     Get all brands that the vendor currently sells.

    Args:
        query (Union[None, Unset, str]):
        page (Union[Unset, int]):  Default: 1.
        size (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, PaginatedResponseBrand]
    """

    return (
        await asyncio_detailed(
            client=client,
            query=query,
            page=page,
            size=size,
        )
    ).parsed
