from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_lookup_table_file_request_data import GetLookupTableFileRequestData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForLookupTableFileApiHandlerType3")


@_attrs_define
class CrudApiRequestAndResponseDataForLookupTableFileApiHandlerType3:
    """
    Attributes:
        read_req (GetLookupTableFileRequestData):
    """

    read_req: "GetLookupTableFileRequestData"

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
        from ..models.get_lookup_table_file_request_data import GetLookupTableFileRequestData

        d = src_dict.copy()
        read_req = GetLookupTableFileRequestData.from_dict(d.pop("ReadReq"))

        crud_api_request_and_response_data_for_lookup_table_file_api_handler_type_3 = cls(
            read_req=read_req,
        )

        return crud_api_request_and_response_data_for_lookup_table_file_api_handler_type_3
