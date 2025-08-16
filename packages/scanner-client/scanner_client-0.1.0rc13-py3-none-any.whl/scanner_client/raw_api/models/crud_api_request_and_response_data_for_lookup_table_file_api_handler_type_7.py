from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.delete_lookup_table_file_response_data import DeleteLookupTableFileResponseData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForLookupTableFileApiHandlerType7")


@_attrs_define
class CrudApiRequestAndResponseDataForLookupTableFileApiHandlerType7:
    """
    Attributes:
        delete_resp (DeleteLookupTableFileResponseData):
    """

    delete_resp: "DeleteLookupTableFileResponseData"

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
        from ..models.delete_lookup_table_file_response_data import DeleteLookupTableFileResponseData

        d = src_dict.copy()
        delete_resp = DeleteLookupTableFileResponseData.from_dict(d.pop("DeleteResp"))

        crud_api_request_and_response_data_for_lookup_table_file_api_handler_type_7 = cls(
            delete_resp=delete_resp,
        )

        return crud_api_request_and_response_data_for_lookup_table_file_api_handler_type_7
