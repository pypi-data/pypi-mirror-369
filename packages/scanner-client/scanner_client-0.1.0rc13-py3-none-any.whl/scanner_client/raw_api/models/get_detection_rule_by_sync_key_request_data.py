from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetDetectionRuleBySyncKeyRequestData")


@_attrs_define
class GetDetectionRuleBySyncKeyRequestData:
    """
    Attributes:
        sync_key (str):
    """

    sync_key: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sync_key = self.sync_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sync_key": sync_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        sync_key = d.pop("sync_key")

        get_detection_rule_by_sync_key_request_data = cls(
            sync_key=sync_key,
        )

        get_detection_rule_by_sync_key_request_data.additional_properties = d
        return get_detection_rule_by_sync_key_request_data

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
