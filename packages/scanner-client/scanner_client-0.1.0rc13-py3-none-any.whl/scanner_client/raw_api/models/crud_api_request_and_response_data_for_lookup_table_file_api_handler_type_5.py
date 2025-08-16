from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.update_lookup_table_file_request_data import UpdateLookupTableFileRequestData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForLookupTableFileApiHandlerType5")


@_attrs_define
class CrudApiRequestAndResponseDataForLookupTableFileApiHandlerType5:
    """
    Attributes:
        update_req (UpdateLookupTableFileRequestData):
    """

    update_req: "UpdateLookupTableFileRequestData"

    def to_dict(self) -> dict[str, Any]:
        update_req = self.update_req.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "UpdateReq": update_req,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.update_lookup_table_file_request_data import UpdateLookupTableFileRequestData

        d = src_dict.copy()
        update_req = UpdateLookupTableFileRequestData.from_dict(d.pop("UpdateReq"))

        crud_api_request_and_response_data_for_lookup_table_file_api_handler_type_5 = cls(
            update_req=update_req,
        )

        return crud_api_request_and_response_data_for_lookup_table_file_api_handler_type_5
