from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.pager_duty_args import PagerDutyArgs


T = TypeVar("T", bound="CreateEventSinkArgsType0")


@_attrs_define
class CreateEventSinkArgsType0:
    """
    Attributes:
        pager_duty (PagerDutyArgs):
    """

    pager_duty: "PagerDutyArgs"

    def to_dict(self) -> dict[str, Any]:
        pager_duty = self.pager_duty.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "PagerDuty": pager_duty,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.pager_duty_args import PagerDutyArgs

        d = src_dict.copy()
        pager_duty = PagerDutyArgs.from_dict(d.pop("PagerDuty"))

        create_event_sink_args_type_0 = cls(
            pager_duty=pager_duty,
        )

        return create_event_sink_args_type_0
