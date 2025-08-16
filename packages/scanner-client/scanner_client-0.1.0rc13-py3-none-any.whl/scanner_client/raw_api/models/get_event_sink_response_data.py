from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.event_sink import EventSink


T = TypeVar("T", bound="GetEventSinkResponseData")


@_attrs_define
class GetEventSinkResponseData:
    """
    Attributes:
        event_sink (EventSink):
    """

    event_sink: "EventSink"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        event_sink = self.event_sink.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "event_sink": event_sink,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.event_sink import EventSink

        d = src_dict.copy()
        event_sink = EventSink.from_dict(d.pop("event_sink"))

        get_event_sink_response_data = cls(
            event_sink=event_sink,
        )

        get_event_sink_response_data.additional_properties = d
        return get_event_sink_response_data

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
