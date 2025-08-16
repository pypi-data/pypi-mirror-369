from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.list_response_with_pagination_for_list_lookup_table_files_response_data import (
    ListResponseWithPaginationForListLookupTableFilesResponseData,
)
from ...types import UNSET, Response


def _get_kwargs(
    *,
    tenant_id: UUID,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_tenant_id = str(tenant_id)
    params["tenant_id"] = json_tenant_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/lookup_table_file",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[ListResponseWithPaginationForListLookupTableFilesResponseData]:
    if response.status_code == 200:
        response_200 = ListResponseWithPaginationForListLookupTableFilesResponseData.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[ListResponseWithPaginationForListLookupTableFilesResponseData]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    tenant_id: UUID,
) -> Response[ListResponseWithPaginationForListLookupTableFilesResponseData]:
    """List lookup table files for a tenant

    Args:
        tenant_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListResponseWithPaginationForListLookupTableFilesResponseData]
    """

    kwargs = _get_kwargs(
        tenant_id=tenant_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    tenant_id: UUID,
) -> Optional[ListResponseWithPaginationForListLookupTableFilesResponseData]:
    """List lookup table files for a tenant

    Args:
        tenant_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListResponseWithPaginationForListLookupTableFilesResponseData
    """

    return sync_detailed(
        client=client,
        tenant_id=tenant_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    tenant_id: UUID,
) -> Response[ListResponseWithPaginationForListLookupTableFilesResponseData]:
    """List lookup table files for a tenant

    Args:
        tenant_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListResponseWithPaginationForListLookupTableFilesResponseData]
    """

    kwargs = _get_kwargs(
        tenant_id=tenant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    tenant_id: UUID,
) -> Optional[ListResponseWithPaginationForListLookupTableFilesResponseData]:
    """List lookup table files for a tenant

    Args:
        tenant_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListResponseWithPaginationForListLookupTableFilesResponseData
    """

    return (
        await asyncio_detailed(
            client=client,
            tenant_id=tenant_id,
        )
    ).parsed
