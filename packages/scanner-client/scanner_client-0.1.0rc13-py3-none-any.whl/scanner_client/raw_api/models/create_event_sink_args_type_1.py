from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.create_slack_event_sink_args import CreateSlackEventSinkArgs


T = TypeVar("T", bound="CreateEventSinkArgsType1")


@_attrs_define
class CreateEventSinkArgsType1:
    """
    Attributes:
        slack (CreateSlackEventSinkArgs):
    """

    slack: "CreateSlackEventSinkArgs"

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
        from ..models.create_slack_event_sink_args import CreateSlackEventSinkArgs

        d = src_dict.copy()
        slack = CreateSlackEventSinkArgs.from_dict(d.pop("Slack"))

        create_event_sink_args_type_1 = cls(
            slack=slack,
        )

        return create_event_sink_args_type_1
