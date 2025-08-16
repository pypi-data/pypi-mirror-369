from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.create_lookup_table_file_request_data import CreateLookupTableFileRequestData


T = TypeVar("T", bound="CrudApiRequestAndResponseDataForLookupTableFileApiHandlerType2")


@_attrs_define
class CrudApiRequestAndResponseDataForLookupTableFileApiHandlerType2:
    """
    Attributes:
        create_req (CreateLookupTableFileRequestData):
    """

    create_req: "CreateLookupTableFileRequestData"

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
        from ..models.create_lookup_table_file_request_data import CreateLookupTableFileRequestData

        d = src_dict.copy()
        create_req = CreateLookupTableFileRequestData.from_dict(d.pop("CreateReq"))

        crud_api_request_and_response_data_for_lookup_table_file_api_handler_type_2 = cls(
            create_req=create_req,
        )

        return crud_api_request_and_response_data_for_lookup_table_file_api_handler_type_2
