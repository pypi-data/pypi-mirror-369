from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateLookupTableFileRequestData")


@_attrs_define
class CreateLookupTableFileRequestData:
    """
    Attributes:
        name (str):
        num_rows (int):
        pending_file_id (UUID):
        size_bytes (int):
        tenant_id (UUID):
        description (Union[None, Unset, str]):
    """

    name: str
    num_rows: int
    pending_file_id: UUID
    size_bytes: int
    tenant_id: UUID
    description: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        num_rows = self.num_rows

        pending_file_id = str(self.pending_file_id)

        size_bytes = self.size_bytes

        tenant_id = str(self.tenant_id)

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "num_rows": num_rows,
                "pending_file_id": pending_file_id,
                "size_bytes": size_bytes,
                "tenant_id": tenant_id,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        num_rows = d.pop("num_rows")

        pending_file_id = UUID(d.pop("pending_file_id"))

        size_bytes = d.pop("size_bytes")

        tenant_id = UUID(d.pop("tenant_id"))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        create_lookup_table_file_request_data = cls(
            name=name,
            num_rows=num_rows,
            pending_file_id=pending_file_id,
            size_bytes=size_bytes,
            tenant_id=tenant_id,
            description=description,
        )

        create_lookup_table_file_request_data.additional_properties = d
        return create_lookup_table_file_request_data

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
