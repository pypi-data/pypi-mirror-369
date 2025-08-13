from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.brand import Brand
from ...models.error_response import ErrorResponse
from ...types import Response


def _get_kwargs(
    brand_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v0/brands/{brand_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Brand, ErrorResponse]]:
    if response.status_code == 200:
        response_200 = Brand.from_dict(response.json())

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
    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Brand, ErrorResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    brand_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Brand, ErrorResponse]]:
    """Get Brand Detail

     Get detailed information for a specific brand by its ID.

    Args:
        brand_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Brand, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        brand_id=brand_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    brand_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Brand, ErrorResponse]]:
    """Get Brand Detail

     Get detailed information for a specific brand by its ID.

    Args:
        brand_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Brand, ErrorResponse]
    """

    return sync_detailed(
        brand_id=brand_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    brand_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Brand, ErrorResponse]]:
    """Get Brand Detail

     Get detailed information for a specific brand by its ID.

    Args:
        brand_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Brand, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        brand_id=brand_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    brand_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Brand, ErrorResponse]]:
    """Get Brand Detail

     Get detailed information for a specific brand by its ID.

    Args:
        brand_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Brand, ErrorResponse]
    """

    return (
        await asyncio_detailed(
            brand_id=brand_id,
            client=client,
        )
    ).parsed
