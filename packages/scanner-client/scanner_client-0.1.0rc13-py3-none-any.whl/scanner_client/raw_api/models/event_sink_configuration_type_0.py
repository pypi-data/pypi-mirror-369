from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="EventSinkConfigurationType0")


@_attrs_define
class EventSinkConfigurationType0:
    """
    Attributes:
        pager_duty (None):
    """

    pager_duty: None

    def to_dict(self) -> dict[str, Any]:
        pager_duty = self.pager_duty

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "PagerDuty": pager_duty,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        pager_duty = d.pop("PagerDuty")

        event_sink_configuration_type_0 = cls(
            pager_duty=pager_duty,
        )

        return event_sink_configuration_type_0
