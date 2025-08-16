import datetime
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="LookupTableFile")


@_attrs_define
class LookupTableFile:
    """
    Attributes:
        created_at (datetime.datetime):
        id (UUID):
        name (str):
        num_rows (int):
        size_bytes (int):
        tenant_id (UUID):
        updated_at (datetime.datetime):
        description (Union[None, Unset, str]):
    """

    created_at: datetime.datetime
    id: UUID
    name: str
    num_rows: int
    size_bytes: int
    tenant_id: UUID
    updated_at: datetime.datetime
    description: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        id = str(self.id)

        name = self.name

        num_rows = self.num_rows

        size_bytes = self.size_bytes

        tenant_id = str(self.tenant_id)

        updated_at = self.updated_at.isoformat()

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "id": id,
                "name": name,
                "num_rows": num_rows,
                "size_bytes": size_bytes,
                "tenant_id": tenant_id,
                "updated_at": updated_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        created_at = isoparse(d.pop("created_at"))

        id = UUID(d.pop("id"))

        name = d.pop("name")

        num_rows = d.pop("num_rows")

        size_bytes = d.pop("size_bytes")

        tenant_id = UUID(d.pop("tenant_id"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        lookup_table_file = cls(
            created_at=created_at,
            id=id,
            name=name,
            num_rows=num_rows,
            size_bytes=size_bytes,
            tenant_id=tenant_id,
            updated_at=updated_at,
            description=description,
        )

        lookup_table_file.additional_properties = d
        return lookup_table_file

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
