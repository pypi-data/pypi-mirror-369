from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_event_sink_request_data import GetEventSinkRequestData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForEventSinkApiHandlerType3")


@_attrs_define
class CrudApiRequestAndResponseDataForEventSinkApiHandlerType3:
    """
    Attributes:
        read_req (GetEventSinkRequestData):
    """

    read_req: "GetEventSinkRequestData"

    def to_dict(self) -> dict[str, Any]:
        read_req = self.read_req.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "ReadReq": read_req,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_event_sink_request_data import GetEventSinkRequestData

        d = src_dict.copy()
        read_req = GetEventSinkRequestData.from_dict(d.pop("ReadReq"))

        crud_api_request_and_response_data_for_event_sink_api_handler_type_3 = cls(
            read_req=read_req,
        )

        return crud_api_request_and_response_data_for_event_sink_api_handler_type_3
