from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.detection_rule_summary import DetectionRuleSummary


T = TypeVar("T", bound="ListDetectionRulesResponseData")


@_attrs_define
class ListDetectionRulesResponseData:
    """
    Attributes:
        detection_rules (list['DetectionRuleSummary']):
    """

    detection_rules: list["DetectionRuleSummary"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        detection_rules = []
        for detection_rules_item_data in self.detection_rules:
            detection_rules_item = detection_rules_item_data.to_dict()
            detection_rules.append(detection_rules_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "detection_rules": detection_rules,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.detection_rule_summary import DetectionRuleSummary

        d = src_dict.copy()
        detection_rules = []
        _detection_rules = d.pop("detection_rules")
        for detection_rules_item_data in _detection_rules:
            detection_rules_item = DetectionRuleSummary.from_dict(detection_rules_item_data)

            detection_rules.append(detection_rules_item)

        list_detection_rules_response_data = cls(
            detection_rules=detection_rules,
        )

        list_detection_rules_response_data.additional_properties = d
        return list_detection_rules_response_data

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
