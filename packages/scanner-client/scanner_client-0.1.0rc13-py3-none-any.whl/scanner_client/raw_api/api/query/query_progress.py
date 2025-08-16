from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.ad_hoc_query_progress_request_data import AdHocQueryProgressRequestData
from ...models.ad_hoc_query_progress_response import AdHocQueryProgressResponse
from ...types import UNSET, Response


def _get_kwargs(
    qr_id: UUID,
    *,
    data: "AdHocQueryProgressRequestData",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_data = data.to_dict()
    params.update(json_data)

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/query_progress/{qr_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[AdHocQueryProgressResponse]:
    if response.status_code == 200:
        response_200 = AdHocQueryProgressResponse.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[AdHocQueryProgressResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    qr_id: UUID,
    *,
    client: AuthenticatedClient,
    data: "AdHocQueryProgressRequestData",
) -> Response[AdHocQueryProgressResponse]:
    """Retrieve the state and current result set of a previously-started query.

    Args:
        qr_id (UUID):
        data (AdHocQueryProgressRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AdHocQueryProgressResponse]
    """

    kwargs = _get_kwargs(
        qr_id=qr_id,
        data=data,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    qr_id: UUID,
    *,
    client: AuthenticatedClient,
    data: "AdHocQueryProgressRequestData",
) -> Optional[AdHocQueryProgressResponse]:
    """Retrieve the state and current result set of a previously-started query.

    Args:
        qr_id (UUID):
        data (AdHocQueryProgressRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AdHocQueryProgressResponse
    """

    return sync_detailed(
        qr_id=qr_id,
        client=client,
        data=data,
    ).parsed


async def asyncio_detailed(
    qr_id: UUID,
    *,
    client: AuthenticatedClient,
    data: "AdHocQueryProgressRequestData",
) -> Response[AdHocQueryProgressResponse]:
    """Retrieve the state and current result set of a previously-started query.

    Args:
        qr_id (UUID):
        data (AdHocQueryProgressRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AdHocQueryProgressResponse]
    """

    kwargs = _get_kwargs(
        qr_id=qr_id,
        data=data,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    qr_id: UUID,
    *,
    client: AuthenticatedClient,
    data: "AdHocQueryProgressRequestData",
) -> Optional[AdHocQueryProgressResponse]:
    """Retrieve the state and current result set of a previously-started query.

    Args:
        qr_id (UUID):
        data (AdHocQueryProgressRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AdHocQueryProgressResponse
    """

    return (
        await asyncio_detailed(
            qr_id=qr_id,
            client=client,
            data=data,
        )
    ).parsed
