from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_detection_rule_request_data import CreateDetectionRuleRequestData
from ...models.get_detection_rule_response_data import GetDetectionRuleResponseData
from ...types import Response


def _get_kwargs(
    *,
    body: CreateDetectionRuleRequestData,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/detection_rule",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[GetDetectionRuleResponseData]:
    if response.status_code == 200:
        response_200 = GetDetectionRuleResponseData.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[GetDetectionRuleResponseData]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: CreateDetectionRuleRequestData,
) -> Response[GetDetectionRuleResponseData]:
    """Create a new detection rule with the specified data.

     If the detection rule is active, it will be immediately scheduled for
    backfill and execution.

    Args:
        body (CreateDetectionRuleRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDetectionRuleResponseData]
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
    body: CreateDetectionRuleRequestData,
) -> Optional[GetDetectionRuleResponseData]:
    """Create a new detection rule with the specified data.

     If the detection rule is active, it will be immediately scheduled for
    backfill and execution.

    Args:
        body (CreateDetectionRuleRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetDetectionRuleResponseData
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: CreateDetectionRuleRequestData,
) -> Response[GetDetectionRuleResponseData]:
    """Create a new detection rule with the specified data.

     If the detection rule is active, it will be immediately scheduled for
    backfill and execution.

    Args:
        body (CreateDetectionRuleRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDetectionRuleResponseData]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: CreateDetectionRuleRequestData,
) -> Optional[GetDetectionRuleResponseData]:
    """Create a new detection rule with the specified data.

     If the detection rule is active, it will be immediately scheduled for
    backfill and execution.

    Args:
        body (CreateDetectionRuleRequestData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetDetectionRuleResponseData
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
