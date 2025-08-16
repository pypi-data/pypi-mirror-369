from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SlackEventSinkConfiguration")


@_attrs_define
class SlackEventSinkConfiguration:
    """
    Attributes:
        channel_id (str): The id of the channel to send messages to.
        channel_name (str): The name of the channel. For display purposes only.
    """

    channel_id: str
    channel_name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        channel_id = self.channel_id

        channel_name = self.channel_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "channel_id": channel_id,
                "channel_name": channel_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        channel_id = d.pop("channel_id")

        channel_name = d.pop("channel_name")

        slack_event_sink_configuration = cls(
            channel_id=channel_id,
            channel_name=channel_name,
        )

        slack_event_sink_configuration.additional_properties = d
        return slack_event_sink_configuration

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
