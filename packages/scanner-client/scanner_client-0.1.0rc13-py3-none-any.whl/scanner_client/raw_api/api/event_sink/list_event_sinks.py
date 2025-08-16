from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.list_event_sinks_request_data import ListEventSinksRequestData
from ...models.list_response_with_pagination_for_list_event_sinks_response_data import (
    ListResponseWithPaginationForListEventSinksResponseData,
)
from ...types import Response


def _get_kwargs(
    *,
    body: ListEventSinksRequestData,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/event_sink",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[ListResponseWithPaginationForListEventSinksResponseData]:
    if response.status_code == 200:
        response_200 = ListResponseWithPaginationForListEventSinksResponseData.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[ListResponseWithPaginationForListEventSinksResponseData]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: ListEventSinksRequestData,
) -> Response[ListResponseWithPaginationForListEventSinksResponseData]:
    """List all event sinks under the provided tenant id.

    Args:
        body (ListEventSinksRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListResponseWithPaginationForListEventSinksResponseData]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: ListEventSinksRequestData,
) -> Optional[ListResponseWithPaginationForListEventSinksResponseData]:
    """List all event sinks under the provided tenant id.

    Args:
        body (ListEventSinksRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListResponseWithPaginationForListEventSinksResponseData
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: ListEventSinksRequestData,
) -> Response[ListResponseWithPaginationForListEventSinksResponseData]:
    """List all event sinks under the provided tenant id.

    Args:
        body (ListEventSinksRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListResponseWithPaginationForListEventSinksResponseData]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: ListEventSinksRequestData,
) -> Optional[ListResponseWithPaginationForListEventSinksResponseData]:
    """List all event sinks under the provided tenant id.

    Args:
        body (ListEventSinksRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListResponseWithPaginationForListEventSinksResponseData
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
