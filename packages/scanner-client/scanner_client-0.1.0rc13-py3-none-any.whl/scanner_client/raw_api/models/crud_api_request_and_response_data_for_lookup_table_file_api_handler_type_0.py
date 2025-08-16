from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.list_lookup_table_files_request_data import ListLookupTableFilesRequestData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForLookupTableFileApiHandlerType0")


@_attrs_define
class CrudApiRequestAndResponseDataForLookupTableFileApiHandlerType0:
    """
    Attributes:
        list_req (ListLookupTableFilesRequestData):
    """

    list_req: "ListLookupTableFilesRequestData"

    def to_dict(self) -> dict[str, Any]:
        list_req = self.list_req.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "ListReq": list_req,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.list_lookup_table_files_request_data import ListLookupTableFilesRequestData

        d = src_dict.copy()
        list_req = ListLookupTableFilesRequestData.from_dict(d.pop("ListReq"))

        crud_api_request_and_response_data_for_lookup_table_file_api_handler_type_0 = cls(
            list_req=list_req,
        )

        return crud_api_request_and_response_data_for_lookup_table_file_api_handler_type_0
