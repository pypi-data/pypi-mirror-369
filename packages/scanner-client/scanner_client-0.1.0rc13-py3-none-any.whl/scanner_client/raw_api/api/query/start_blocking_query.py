from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.ad_hoc_query_progress_response import AdHocQueryProgressResponse
from ...models.start_ad_hoc_query_request_data import StartAdHocQueryRequestData
from ...types import Response


def _get_kwargs(
    *,
    body: StartAdHocQueryRequestData,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/blocking_query",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    *,
    client: AuthenticatedClient,
    body: StartAdHocQueryRequestData,
) -> Response[AdHocQueryProgressResponse]:
    """Start a new blocking query. This will directly return the search results,

     blocking the connection until it has completed, but will time out after 60
    seconds.

    Args:
        body (StartAdHocQueryRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AdHocQueryProgressResponse]
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
    body: StartAdHocQueryRequestData,
) -> Optional[AdHocQueryProgressResponse]:
    """Start a new blocking query. This will directly return the search results,

     blocking the connection until it has completed, but will time out after 60
    seconds.

    Args:
        body (StartAdHocQueryRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AdHocQueryProgressResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: StartAdHocQueryRequestData,
) -> Response[AdHocQueryProgressResponse]:
    """Start a new blocking query. This will directly return the search results,

     blocking the connection until it has completed, but will time out after 60
    seconds.

    Args:
        body (StartAdHocQueryRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AdHocQueryProgressResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: StartAdHocQueryRequestData,
) -> Optional[AdHocQueryProgressResponse]:
    """Start a new blocking query. This will directly return the search results,

     blocking the connection until it has completed, but will time out after 60
    seconds.

    Args:
        body (StartAdHocQueryRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AdHocQueryProgressResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
