from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.list_detection_rules_request_data import ListDetectionRulesRequestData
from ...models.list_response_with_pagination_for_list_detection_rules_response_data import (
    ListResponseWithPaginationForListDetectionRulesResponseData,
)
from ...types import Response


def _get_kwargs(
    *,
    body: ListDetectionRulesRequestData,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/detection_rule",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[ListResponseWithPaginationForListDetectionRulesResponseData]:
    if response.status_code == 200:
        response_200 = ListResponseWithPaginationForListDetectionRulesResponseData.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[ListResponseWithPaginationForListDetectionRulesResponseData]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: ListDetectionRulesRequestData,
) -> Response[ListResponseWithPaginationForListDetectionRulesResponseData]:
    """List all detection rules under the provided tenant id.

    Args:
        body (ListDetectionRulesRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListResponseWithPaginationForListDetectionRulesResponseData]
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
    body: ListDetectionRulesRequestData,
) -> Optional[ListResponseWithPaginationForListDetectionRulesResponseData]:
    """List all detection rules under the provided tenant id.

    Args:
        body (ListDetectionRulesRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListResponseWithPaginationForListDetectionRulesResponseData
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: ListDetectionRulesRequestData,
) -> Response[ListResponseWithPaginationForListDetectionRulesResponseData]:
    """List all detection rules under the provided tenant id.

    Args:
        body (ListDetectionRulesRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListResponseWithPaginationForListDetectionRulesResponseData]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: ListDetectionRulesRequestData,
) -> Optional[ListResponseWithPaginationForListDetectionRulesResponseData]:
    """List all detection rules under the provided tenant id.

    Args:
        body (ListDetectionRulesRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListResponseWithPaginationForListDetectionRulesResponseData
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
