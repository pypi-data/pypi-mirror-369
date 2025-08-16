from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AdHocQueryProgressMetadata")


@_attrs_define
class AdHocQueryProgressMetadata:
    """
    Attributes:
        n_bytes_scanned (int):
    """

    n_bytes_scanned: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        n_bytes_scanned = self.n_bytes_scanned

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "n_bytes_scanned": n_bytes_scanned,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        n_bytes_scanned = d.pop("n_bytes_scanned")

        ad_hoc_query_progress_metadata = cls(
            n_bytes_scanned=n_bytes_scanned,
        )

        ad_hoc_query_progress_metadata.additional_properties = d
        return ad_hoc_query_progress_metadata

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
