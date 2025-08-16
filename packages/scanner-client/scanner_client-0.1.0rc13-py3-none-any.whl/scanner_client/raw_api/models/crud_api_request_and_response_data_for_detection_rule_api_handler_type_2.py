from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.create_detection_rule_request_data import CreateDetectionRuleRequestData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForDetectionRuleApiHandlerType2")


@_attrs_define
class CrudApiRequestAndResponseDataForDetectionRuleApiHandlerType2:
    """
    Attributes:
        create_req (CreateDetectionRuleRequestData):
    """

    create_req: "CreateDetectionRuleRequestData"

    def to_dict(self) -> dict[str, Any]:
        create_req = self.create_req.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "CreateReq": create_req,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_detection_rule_request_data import CreateDetectionRuleRequestData

        d = src_dict.copy()
        create_req = CreateDetectionRuleRequestData.from_dict(d.pop("CreateReq"))

        crud_api_request_and_response_data_for_detection_rule_api_handler_type_2 = cls(
            create_req=create_req,
        )

        return crud_api_request_and_response_data_for_detection_rule_api_handler_type_2
