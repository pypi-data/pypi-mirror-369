from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.slack_event_sink_configuration import SlackEventSinkConfiguration


T = TypeVar("T", bound="EventSinkConfigurationType1")


@_attrs_define
class EventSinkConfigurationType1:
    """
    Attributes:
        slack (SlackEventSinkConfiguration):
    """

    slack: "SlackEventSinkConfiguration"

    def to_dict(self) -> dict[str, Any]:
        slack = self.slack.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "Slack": slack,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.slack_event_sink_configuration import SlackEventSinkConfiguration

        d = src_dict.copy()
        slack = SlackEventSinkConfiguration.from_dict(d.pop("Slack"))

        event_sink_configuration_type_1 = cls(
            slack=slack,
        )

        return event_sink_configuration_type_1
