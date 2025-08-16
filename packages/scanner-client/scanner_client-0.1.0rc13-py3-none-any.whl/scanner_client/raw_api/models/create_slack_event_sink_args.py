from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateSlackEventSinkArgs")


@_attrs_define
class CreateSlackEventSinkArgs:
    """
    Attributes:
        slack_integration_id (UUID):
        channel (Union[None, Unset, str]):
        channel_id (Union[None, Unset, str]):
    """

    slack_integration_id: UUID
    channel: Union[None, Unset, str] = UNSET
    channel_id: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        slack_integration_id = str(self.slack_integration_id)

        channel: Union[None, Unset, str]
        if isinstance(self.channel, Unset):
            channel = UNSET
        else:
            channel = self.channel

        channel_id: Union[None, Unset, str]
        if isinstance(self.channel_id, Unset):
            channel_id = UNSET
        else:
            channel_id = self.channel_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "slack_integration_id": slack_integration_id,
            }
        )
        if channel is not UNSET:
            field_dict["channel"] = channel
        if channel_id is not UNSET:
            field_dict["channel_id"] = channel_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        slack_integration_id = UUID(d.pop("slack_integration_id"))

        def _parse_channel(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        channel = _parse_channel(d.pop("channel", UNSET))

        def _parse_channel_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        channel_id = _parse_channel_id(d.pop("channel_id", UNSET))

        create_slack_event_sink_args = cls(
            slack_integration_id=slack_integration_id,
            channel=channel,
            channel_id=channel_id,
        )

        create_slack_event_sink_args.additional_properties = d
        return create_slack_event_sink_args

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
