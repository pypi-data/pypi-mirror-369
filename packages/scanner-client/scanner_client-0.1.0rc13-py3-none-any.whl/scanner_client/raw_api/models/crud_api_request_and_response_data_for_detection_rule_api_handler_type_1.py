from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.list_response_with_pagination_for_list_detection_rules_response_data import (
        ListResponseWithPaginationForListDetectionRulesResponseData,
    )


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForDetectionRuleApiHandlerType1")


@_attrs_define
class CrudApiRequestAndResponseDataForDetectionRuleApiHandlerType1:
    """
    Attributes:
        list_resp (ListResponseWithPaginationForListDetectionRulesResponseData):
    """

    list_resp: "ListResponseWithPaginationForListDetectionRulesResponseData"

    def to_dict(self) -> dict[str, Any]:
        list_resp = self.list_resp.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "ListResp": list_resp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.list_response_with_pagination_for_list_detection_rules_response_data import (
            ListResponseWithPaginationForListDetectionRulesResponseData,
        )

        d = src_dict.copy()
        list_resp = ListResponseWithPaginationForListDetectionRulesResponseData.from_dict(d.pop("ListResp"))

        crud_api_request_and_response_data_for_detection_rule_api_handler_type_1 = cls(
            list_resp=list_resp,
        )

        return crud_api_request_and_response_data_for_detection_rule_api_handler_type_1
