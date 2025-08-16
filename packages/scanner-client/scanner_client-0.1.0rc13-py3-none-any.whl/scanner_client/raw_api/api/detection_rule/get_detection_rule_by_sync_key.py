from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_detection_rule_summary_response_data import GetDetectionRuleSummaryResponseData
from ...types import Response


def _get_kwargs(
    sync_key: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/detection_rule_by_sync_key/{sync_key}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[GetDetectionRuleSummaryResponseData]:
    if response.status_code == 200:
        response_200 = GetDetectionRuleSummaryResponseData.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[GetDetectionRuleSummaryResponseData]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    sync_key: str,
    *,
    client: AuthenticatedClient,
) -> Response[GetDetectionRuleSummaryResponseData]:
    """Get the detection rule with the provided sync key.

     This is intended for the use case of automatically-syncing detection rules to
    yaml files (usually via the scanner CLI tool).

    Args:
        sync_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDetectionRuleSummaryResponseData]
    """

    kwargs = _get_kwargs(
        sync_key=sync_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    sync_key: str,
    *,
    client: AuthenticatedClient,
) -> Optional[GetDetectionRuleSummaryResponseData]:
    """Get the detection rule with the provided sync key.

     This is intended for the use case of automatically-syncing detection rules to
    yaml files (usually via the scanner CLI tool).

    Args:
        sync_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetDetectionRuleSummaryResponseData
    """

    return sync_detailed(
        sync_key=sync_key,
        client=client,
    ).parsed


async def asyncio_detailed(
    sync_key: str,
    *,
    client: AuthenticatedClient,
) -> Response[GetDetectionRuleSummaryResponseData]:
    """Get the detection rule with the provided sync key.

     This is intended for the use case of automatically-syncing detection rules to
    yaml files (usually via the scanner CLI tool).

    Args:
        sync_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDetectionRuleSummaryResponseData]
    """

    kwargs = _get_kwargs(
        sync_key=sync_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    sync_key: str,
    *,
    client: AuthenticatedClient,
) -> Optional[GetDetectionRuleSummaryResponseData]:
    """Get the detection rule with the provided sync key.

     This is intended for the use case of automatically-syncing detection rules to
    yaml files (usually via the scanner CLI tool).

    Args:
        sync_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetDetectionRuleSummaryResponseData
    """

    return (
        await asyncio_detailed(
            sync_key=sync_key,
            client=client,
        )
    ).parsed
