from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_detection_rule_response_data import GetDetectionRuleResponseData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForDetectionRuleApiHandlerType4")


@_attrs_define
class CrudApiRequestAndResponseDataForDetectionRuleApiHandlerType4:
    """
    Attributes:
        read_resp (GetDetectionRuleResponseData):
    """

    read_resp: "GetDetectionRuleResponseData"

    def to_dict(self) -> dict[str, Any]:
        read_resp = self.read_resp.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "ReadResp": read_resp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_detection_rule_response_data import GetDetectionRuleResponseData

        d = src_dict.copy()
        read_resp = GetDetectionRuleResponseData.from_dict(d.pop("ReadResp"))

        crud_api_request_and_response_data_for_detection_rule_api_handler_type_4 = cls(
            read_resp=read_resp,
        )

        return crud_api_request_and_response_data_for_detection_rule_api_handler_type_4
