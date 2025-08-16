from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.update_slack_event_sink_args import UpdateSlackEventSinkArgs


T = TypeVar("T", bound="UpdateEventSinkArgsType1")


@_attrs_define
class UpdateEventSinkArgsType1:
    """
    Attributes:
        slack (UpdateSlackEventSinkArgs):
    """

    slack: "UpdateSlackEventSinkArgs"

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
        from ..models.update_slack_event_sink_args import UpdateSlackEventSinkArgs

        d = src_dict.copy()
        slack = UpdateSlackEventSinkArgs.from_dict(d.pop("Slack"))

        update_event_sink_args_type_1 = cls(
            slack=slack,
        )

        return update_event_sink_args_type_1
