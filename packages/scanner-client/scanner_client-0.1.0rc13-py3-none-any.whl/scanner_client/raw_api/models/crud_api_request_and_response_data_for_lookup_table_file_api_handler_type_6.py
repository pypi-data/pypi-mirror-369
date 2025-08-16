from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.delete_lookup_table_file_request_data import DeleteLookupTableFileRequestData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForLookupTableFileApiHandlerType6")


@_attrs_define
class CrudApiRequestAndResponseDataForLookupTableFileApiHandlerType6:
    """
    Attributes:
        delete_req (DeleteLookupTableFileRequestData):
    """

    delete_req: "DeleteLookupTableFileRequestData"

    def to_dict(self) -> dict[str, Any]:
        delete_req = self.delete_req.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "DeleteReq": delete_req,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.delete_lookup_table_file_request_data import DeleteLookupTableFileRequestData

        d = src_dict.copy()
        delete_req = DeleteLookupTableFileRequestData.from_dict(d.pop("DeleteReq"))

        crud_api_request_and_response_data_for_lookup_table_file_api_handler_type_6 = cls(
            delete_req=delete_req,
        )

        return crud_api_request_and_response_data_for_lookup_table_file_api_handler_type_6
