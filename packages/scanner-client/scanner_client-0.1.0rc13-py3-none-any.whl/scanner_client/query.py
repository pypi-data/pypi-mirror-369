import time
import uuid

from .http_err import get_body_and_handle_err
from .raw_api.api.query import query_progress, start_blocking_query, start_query
from .raw_api.client import AuthenticatedClient
from .raw_api.models import (
    AdHocQueryProgressRequestData,
    AdHocQueryProgressResponse,
    LogEventId,
    StartAdHocQueryRequestData,
    StartAdHocQueryResponse,
)
from .raw_api.types import Unset, UNSET


class Query:
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def start_query(
        self,
        query_text: str,
        start_time: str | Unset = UNSET,
        end_time: str | Unset = UNSET,
        start_leid: LogEventId | Unset = UNSET,
        end_leid: LogEventId | Unset = UNSET,
        scan_back_to_front: bool | Unset = UNSET,
        max_rows: int | Unset = UNSET,
        max_bytes: int | Unset = UNSET,
    ) -> StartAdHocQueryResponse:
        req_data = StartAdHocQueryRequestData(
            query=query_text,
            start_time=start_time,
            end_time=end_time,
            start_leid=start_leid,
            end_leid=end_leid,
            scan_back_to_front=scan_back_to_front,
            max_rows=max_rows,
            max_bytes=max_bytes,
        )

        resp = start_query.sync_detailed(client=self._client, body=req_data)

        return get_body_and_handle_err(resp)

    def query_progress(
        self,
        qr_id: str,
        show_intermediate_results: bool | Unset = UNSET,
    ) -> AdHocQueryProgressResponse:
        data = AdHocQueryProgressRequestData(
            show_intermediate_results=show_intermediate_results
        )
        resp = query_progress.sync_detailed(uuid.UUID(qr_id), client=self._client, data=data)

        return get_body_and_handle_err(resp)

    def blocking_query(
        self,
        query_text: str,
        start_time: str | Unset = UNSET,
        end_time: str | Unset = UNSET,
        start_leid: LogEventId | Unset = UNSET,
        end_leid: LogEventId | Unset = UNSET,
        scan_back_to_front: bool | Unset = UNSET,
        max_rows: int | Unset = UNSET,
        max_bytes: int | Unset = UNSET,
    ) -> AdHocQueryProgressResponse:
        req_data = StartAdHocQueryRequestData(
            query=query_text,
            start_time=start_time,
            end_time=end_time,
            start_leid=start_leid,
            end_leid=end_leid,
            scan_back_to_front=scan_back_to_front,
            max_rows=max_rows,
            max_bytes=max_bytes,
        )

        resp = start_blocking_query.sync_detailed(client=self._client, body=req_data)

        return get_body_and_handle_err(resp)

    # Handles `start_query` and `query_progress` loop for non-blocking queries.
    def start_query_and_return_results(
        self,
        query_text: str,
        start_time: str | Unset = UNSET,
        end_time: str | Unset = UNSET,
        start_leid: LogEventId | Unset = UNSET,
        end_leid: LogEventId | Unset = UNSET,
        scan_back_to_front: bool | Unset = UNSET,
        max_rows: int | Unset = UNSET,
        max_bytes: int | Unset = UNSET,
    ) -> AdHocQueryProgressResponse:
        qr_id = self.start_query(
            query_text,
            start_time,
            end_time,
            start_leid,
            end_leid,
            scan_back_to_front,
            max_rows,
            max_bytes,
        ).qr_id

        while True:
            query_progress = self.query_progress(str(qr_id), False)
            if query_progress.is_completed:
                return query_progress

            time.sleep(1)


class AsyncQuery:
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def start_query(
        self,
        query_text: str,
        start_time: str | Unset = UNSET,
        end_time: str | Unset = UNSET,
        start_leid: LogEventId | Unset = UNSET,
        end_leid: LogEventId | Unset = UNSET,
        scan_back_to_front: bool | Unset = UNSET,
        max_rows: int | Unset = UNSET,
        max_bytes: int | Unset = UNSET,
    ) -> StartAdHocQueryResponse:
        req_data = StartAdHocQueryRequestData(
            query=query_text,
            start_time=start_time,
            end_time=end_time,
            start_leid=start_leid,
            end_leid=end_leid,
            scan_back_to_front=scan_back_to_front,
            max_rows=max_rows,
            max_bytes=max_bytes,
        )

        resp = await start_query.asyncio_detailed(client=self._client, body=req_data)

        return get_body_and_handle_err(resp)

    async def query_progress(
        self,
        qr_id: str,
        show_intermediate_results: bool | Unset = UNSET,
    ) -> AdHocQueryProgressResponse:
        data = AdHocQueryProgressRequestData(
            show_intermediate_results=show_intermediate_results
        )
        resp = await query_progress.asyncio_detailed(
            uuid.UUID(qr_id), client=self._client, data=data
        )

        return get_body_and_handle_err(resp)

    async def blocking_query(
        self,
        query_text: str,
        start_time: str | Unset = UNSET,
        end_time: str | Unset = UNSET,
        start_leid: LogEventId | Unset = UNSET,
        end_leid: LogEventId | Unset = UNSET,
        scan_back_to_front: bool | Unset = UNSET,
        max_rows: int | Unset = UNSET,
        max_bytes: int | Unset = UNSET,
    ) -> AdHocQueryProgressResponse:
        req_data = StartAdHocQueryRequestData(
            query=query_text,
            start_time=start_time,
            end_time=end_time,
            start_leid=start_leid,
            end_leid=end_leid,
            scan_back_to_front=scan_back_to_front,
            max_rows=max_rows,
            max_bytes=max_bytes,
        )

        resp = await start_blocking_query.asyncio_detailed(
            client=self._client, body=req_data
        )

        return get_body_and_handle_err(resp)

    # Handles `start_query` and `query_progress` loop for non-blocking queries.
    async def start_query_and_return_results(
        self,
        query_text: str,
        start_time: str | Unset = UNSET,
        end_time: str | Unset = UNSET,
        start_leid: LogEventId | Unset = UNSET,
        end_leid: LogEventId | Unset = UNSET,
        scan_back_to_front: bool | Unset = UNSET,
        max_rows: int | Unset = UNSET,
        max_bytes: int | Unset = UNSET,
    ) -> AdHocQueryProgressResponse:
        resp = await self.start_query(
            query_text,
            start_time,
            end_time,
            start_leid,
            end_leid,
            scan_back_to_front,
            max_rows,
            max_bytes,
        )

        while True:
            query_progress = await self.query_progress(str(resp.qr_id), False)
            if query_progress.is_completed:
                return query_progress

            time.sleep(1)
