from typing import AsyncGenerator, Generator, Optional

import uuid

from .http_err import get_body_and_handle_err
from .raw_api.api.detection_rule import (
    list_detection_rules,
    create_detection_rule,
    get_detection_rule,
    get_detection_rule_by_sync_key,
    update_detection_rule,
    delete_detection_rule,
)
from .raw_api.models import (
    ListDetectionRulesRequestData,
    CreateDetectionRuleRequestData,
    DeleteDetectionRuleResponseData,
    DetectionRule as DetectionRuleJson,
    DetectionRuleSummary,
    ListResponseWithPaginationForListDetectionRulesResponseData,
    UpdateDetectionRuleRequestData,
    DetectionSeverityType0,
    DetectionSeverityType1,
    DetectionSeverityType2,
    DetectionSeverityType3,
    DetectionSeverityType4,
    DetectionSeverityType5,
    DetectionSeverityType6,
    DetectionSeverityType7,
    PermsByRoleForRbacDetectionRulePermissionType,
    PermsByRoleForRbacDetectionRulePermissionTypePermissionsByRole,
    RbacDetectionRulePermissionType,
    DetectionRuleSortOrder,
    PaginationMetadata,
    PaginationParameters,
)
from .raw_api.client import AuthenticatedClient
from .raw_api.types import Unset, UNSET

# TODO: this is currently kinda awkward to deal with. Ideally we can get the
# openapi schema to just include a single DetectionSeverity enum, instead of a
# union type across 7 enums each with one variant.
DetectionSeverity = (
    DetectionSeverityType0
    | DetectionSeverityType1
    | DetectionSeverityType2
    | DetectionSeverityType3
    | DetectionSeverityType4
    | DetectionSeverityType5
    | DetectionSeverityType6
    | DetectionSeverityType7
)


def string_to_detection_severity(severity: str) -> DetectionSeverity:
    if severity == "Informational":
        return DetectionSeverityType1.INFORMATIONAL
    elif severity == "Low":
        return DetectionSeverityType2.LOW
    elif severity == "Medium":
        return DetectionSeverityType3.MEDIUM
    elif severity == "High":
        return DetectionSeverityType4.HIGH
    elif severity == "Critical":
        return DetectionSeverityType5.CRITICAL
    elif severity == "Fatal":
        return DetectionSeverityType6.FATAL
    elif severity == "Other":
        return DetectionSeverityType7.OTHER
    else:
        return DetectionSeverityType0.UNKNOWN


def starting_permissions_for_detection_rule(
    starting_permissions: dict[str, list[RbacDetectionRulePermissionType]],
) -> PermsByRoleForRbacDetectionRulePermissionType:
    return PermsByRoleForRbacDetectionRulePermissionType(
        permissions_by_role=PermsByRoleForRbacDetectionRulePermissionTypePermissionsByRole.from_dict(
            starting_permissions
        ),
    )


def pagination_parameters(
    page_token: Optional[str] | Unset = UNSET, page_size: int | Unset = UNSET
) -> PaginationParameters:
    return PaginationParameters(
        page_token=page_token,
        page_size=page_size,
    )


class DetectionRule:
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client


    def list_all(
        self,
        tenant_id: str,
        pagination: Optional[PaginationParameters] | Unset = UNSET,
        sort_order: Optional[DetectionRuleSortOrder] | Unset = UNSET,
    ) -> ListResponseWithPaginationForListDetectionRulesResponseData:
        req_body = ListDetectionRulesRequestData(
            tenant_id=uuid.UUID(tenant_id),
            pagination=pagination,
            sort_order=sort_order,
        )

        resp = list_detection_rules.sync_detailed(client=self._client, body=req_body)

        resp_body = get_body_and_handle_err(resp)

        return resp_body


    def list_all_iter(
        self,
        tenant_id: str
    ) -> Generator[DetectionRuleSummary, None, None]:
        resp = self.list_all(tenant_id)
        yield from resp.data.detection_rules

        pagination = resp.pagination
        while isinstance(pagination, PaginationMetadata):
            # If there is a next page, get next page.
            # Otherwise, return.
            if isinstance(pagination.next_page_token, str):
                next_pagination_params = pagination_parameters(
                    pagination.next_page_token
                )
                next_resp = self.list_all(tenant_id, next_pagination_params)

                yield from next_resp.data.detection_rules

                pagination = next_resp.pagination
            else:
                return


    def create(
        self,
        tenant_id: str,
        name: str,
        description: str,
        time_range_s: int,
        run_frequency_s: int,
        enabled: bool,
        severity: DetectionSeverity,
        query_text: str,
        event_sink_ids: list[str],
        starting_permissions: (
            Optional[PermsByRoleForRbacDetectionRulePermissionType] | Unset
        ) = UNSET,
        sync_key: Optional[str] | Unset = UNSET,
    ) -> DetectionRuleJson:
        req_body = CreateDetectionRuleRequestData(
            tenant_id=uuid.UUID(tenant_id),
            name=name,
            description=description,
            time_range_s=time_range_s,
            run_frequency_s=run_frequency_s,
            enabled=enabled,
            severity=severity,
            query_text=query_text,
            event_sink_ids=[uuid.UUID(id) for id in event_sink_ids],
            starting_permissions=starting_permissions,
            sync_key=sync_key,
        )

        resp = create_detection_rule.sync_detailed(client=self._client, body=req_body)

        resp_body = get_body_and_handle_err(resp)

        return resp_body.detection_rule

    def get(self, detection_rule_id: str) -> DetectionRuleJson:
        resp = get_detection_rule.sync_detailed(
            uuid.UUID(detection_rule_id), client=self._client
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.detection_rule

    def get_by_sync_key(self, sync_key: str) -> DetectionRuleSummary:
        resp = get_detection_rule_by_sync_key.sync_detailed(
            sync_key, client=self._client
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.detection_rule

    def update(
        self,
        detection_rule_id: str,
        name: str | Unset = UNSET,
        description: str | Unset = UNSET,
        time_range_s: int | Unset = UNSET,
        run_frequency_s: int | Unset = UNSET,
        enabled: bool | Unset = UNSET,
        severity: DetectionSeverity | Unset = UNSET,
        query_text: str | Unset = UNSET,
        event_sink_ids: list[str] | Unset = UNSET,
        sync_key: Optional[str] | Unset = UNSET,
    ) -> DetectionRuleJson:
        req_body = UpdateDetectionRuleRequestData(
            id=uuid.UUID(detection_rule_id),
            name=name,
            description=description,
            time_range_s=time_range_s,
            run_frequency_s=run_frequency_s,
            enabled=enabled,
            severity=severity,
            query_text=query_text,
            event_sink_ids=(
                [uuid.UUID(id) for id in event_sink_ids]
                if isinstance(event_sink_ids, list)
                else UNSET
            ),
            sync_key=sync_key,
        )

        resp = update_detection_rule.sync_detailed(
            uuid.UUID(detection_rule_id), client=self._client, body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.detection_rule

    def delete(self, detection_rule_id: str) -> DeleteDetectionRuleResponseData:
        resp = delete_detection_rule.sync_detailed(
            uuid.UUID(detection_rule_id), client=self._client
        )

        return get_body_and_handle_err(resp)


class AsyncDetectionRule:
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def list_all(
        self,
        tenant_id: str,
        pagination: Optional[PaginationParameters] | Unset = UNSET,
        sort_order: Optional[DetectionRuleSortOrder] | Unset = UNSET,
    ) -> ListResponseWithPaginationForListDetectionRulesResponseData:
        req_body = ListDetectionRulesRequestData(
            tenant_id=uuid.UUID(tenant_id),
            pagination=pagination,
            sort_order=sort_order,
        )

        resp = await list_detection_rules.asyncio_detailed(
            client=self._client, body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body


    async def list_all_iter(
        self,
        tenant_id: str
    ) -> AsyncGenerator[DetectionRuleSummary, None]:
        resp = await self.list_all(tenant_id)

        for detection_rule in resp.data.detection_rules:
            yield detection_rule

        pagination = resp.pagination
        while isinstance(pagination, PaginationMetadata):
            # If there is a next page, get next page.
            # Otherwise, return.
            if isinstance(pagination.next_page_token, str):
                next_pagination_params = pagination_parameters(
                    pagination.next_page_token
                )
                next_resp = await self.list_all(tenant_id, next_pagination_params)

                for detection_rule in next_resp.data.detection_rules:
                    yield detection_rule

                pagination = next_resp.pagination
            else:
                return


    async def create(
        self,
        tenant_id: str,
        name: str,
        description: str,
        time_range_s: int,
        run_frequency_s: int,
        enabled: bool,
        severity: DetectionSeverity,
        query_text: str,
        event_sink_ids: list[str],
        sync_key: Optional[str] | Unset = UNSET,
    ) -> DetectionRuleJson:
        req_body = CreateDetectionRuleRequestData(
            tenant_id=uuid.UUID(tenant_id),
            name=name,
            description=description,
            time_range_s=time_range_s,
            run_frequency_s=run_frequency_s,
            enabled=enabled,
            severity=severity,
            query_text=query_text,
            event_sink_ids=[uuid.UUID(id) for id in event_sink_ids],
            sync_key=sync_key,
        )

        resp = await create_detection_rule.asyncio_detailed(
            client=self._client, body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.detection_rule

    async def get(self, detection_rule_id: str) -> DetectionRuleJson:
        resp = await get_detection_rule.asyncio_detailed(
            uuid.UUID(detection_rule_id), client=self._client
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.detection_rule

    async def get_by_sync_key(self, sync_key: str) -> DetectionRuleSummary:
        resp = await get_detection_rule_by_sync_key.asyncio_detailed(
            sync_key, client=self._client
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.detection_rule

    async def update(
        self,
        detection_rule_id: str,
        name: str | Unset = UNSET,
        description: str | Unset = UNSET,
        time_range_s: int | Unset = UNSET,
        run_frequency_s: int | Unset = UNSET,
        enabled: bool | Unset = UNSET,
        severity: DetectionSeverity | Unset = UNSET,
        query_text: str | Unset = UNSET,
        event_sink_ids: list[str] | Unset = UNSET,
        sync_key: Optional[str] | Unset = UNSET,
    ) -> DetectionRuleJson:
        req_body = UpdateDetectionRuleRequestData(
            id=uuid.UUID(detection_rule_id),
            name=name,
            description=description,
            time_range_s=time_range_s,
            run_frequency_s=run_frequency_s,
            enabled=enabled,
            severity=severity,
            query_text=query_text,
            event_sink_ids=(
                [uuid.UUID(id) for id in event_sink_ids]
                if isinstance(event_sink_ids, list)
                else UNSET
            ),
            sync_key=sync_key,
        )

        resp = await update_detection_rule.asyncio_detailed(
            uuid.UUID(detection_rule_id), client=self._client, body=req_body
        )

        resp_body = get_body_and_handle_err(resp)

        return resp_body.detection_rule

    async def delete(self, detection_rule_id: str) -> DeleteDetectionRuleResponseData:
        resp = await delete_detection_rule.asyncio_detailed(
            uuid.UUID(detection_rule_id), client=self._client
        )

        return get_body_and_handle_err(resp)
