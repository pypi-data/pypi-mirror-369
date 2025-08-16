from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.lookup_table_file import LookupTableFile


T = TypeVar("T", bound="ListLookupTableFilesResponseData")


@_attrs_define
class ListLookupTableFilesResponseData:
    """
    Attributes:
        lookup_table_files (list['LookupTableFile']):
    """

    lookup_table_files: list["LookupTableFile"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        lookup_table_files = []
        for lookup_table_files_item_data in self.lookup_table_files:
            lookup_table_files_item = lookup_table_files_item_data.to_dict()
            lookup_table_files.append(lookup_table_files_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "lookup_table_files": lookup_table_files,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.lookup_table_file import LookupTableFile

        d = src_dict.copy()
        lookup_table_files = []
        _lookup_table_files = d.pop("lookup_table_files")
        for lookup_table_files_item_data in _lookup_table_files:
            lookup_table_files_item = LookupTableFile.from_dict(lookup_table_files_item_data)

            lookup_table_files.append(lookup_table_files_item)

        list_lookup_table_files_response_data = cls(
            lookup_table_files=lookup_table_files,
        )

        list_lookup_table_files_response_data.additional_properties = d
        return list_lookup_table_files_response_data

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
