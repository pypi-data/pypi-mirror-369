from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.list_response_with_pagination_for_list_lookup_table_files_response_data import (
        ListResponseWithPaginationForListLookupTableFilesResponseData,
    )


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForLookupTableFileApiHandlerType1")


@_attrs_define
class CrudApiRequestAndResponseDataForLookupTableFileApiHandlerType1:
    """
    Attributes:
        list_resp (ListResponseWithPaginationForListLookupTableFilesResponseData):
    """

    list_resp: "ListResponseWithPaginationForListLookupTableFilesResponseData"

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
        from ..models.list_response_with_pagination_for_list_lookup_table_files_response_data import (
            ListResponseWithPaginationForListLookupTableFilesResponseData,
        )

        d = src_dict.copy()
        list_resp = ListResponseWithPaginationForListLookupTableFilesResponseData.from_dict(d.pop("ListResp"))

        crud_api_request_and_response_data_for_lookup_table_file_api_handler_type_1 = cls(
            list_resp=list_resp,
        )

        return crud_api_request_and_response_data_for_lookup_table_file_api_handler_type_1
