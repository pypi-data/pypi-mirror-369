from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.delete_event_sink_response_data import DeleteEventSinkResponseData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForEventSinkApiHandlerType7")


@_attrs_define
class CrudApiRequestAndResponseDataForEventSinkApiHandlerType7:
    """
    Attributes:
        delete_resp (DeleteEventSinkResponseData):
    """

    delete_resp: "DeleteEventSinkResponseData"

    def to_dict(self) -> dict[str, Any]:
        delete_resp = self.delete_resp.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "DeleteResp": delete_resp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.delete_event_sink_response_data import DeleteEventSinkResponseData

        d = src_dict.copy()
        delete_resp = DeleteEventSinkResponseData.from_dict(d.pop("DeleteResp"))

        crud_api_request_and_response_data_for_event_sink_api_handler_type_7 = cls(
            delete_resp=delete_resp,
        )

        return crud_api_request_and_response_data_for_event_sink_api_handler_type_7
