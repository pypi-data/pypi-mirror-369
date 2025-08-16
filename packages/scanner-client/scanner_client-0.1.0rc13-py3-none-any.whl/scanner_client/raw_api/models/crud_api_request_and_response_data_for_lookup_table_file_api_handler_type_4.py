from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_lookup_table_file_response_data import GetLookupTableFileResponseData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForLookupTableFileApiHandlerType4")


@_attrs_define
class CrudApiRequestAndResponseDataForLookupTableFileApiHandlerType4:
    """
    Attributes:
        read_resp (GetLookupTableFileResponseData):
    """

    read_resp: "GetLookupTableFileResponseData"

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
        from ..models.get_lookup_table_file_response_data import GetLookupTableFileResponseData

        d = src_dict.copy()
        read_resp = GetLookupTableFileResponseData.from_dict(d.pop("ReadResp"))

        crud_api_request_and_response_data_for_lookup_table_file_api_handler_type_4 = cls(
            read_resp=read_resp,
        )

        return crud_api_request_and_response_data_for_lookup_table_file_api_handler_type_4
