from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.webhook_args import WebhookArgs


T = TypeVar("T", bound="CreateEventSinkArgsType2")


@_attrs_define
class CreateEventSinkArgsType2:
    """
    Attributes:
        webhook (WebhookArgs):
    """

    webhook: "WebhookArgs"

    def to_dict(self) -> dict[str, Any]:
        webhook = self.webhook.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "Webhook": webhook,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.webhook_args import WebhookArgs

        d = src_dict.copy()
        webhook = WebhookArgs.from_dict(d.pop("Webhook"))

        create_event_sink_args_type_2 = cls(
            webhook=webhook,
        )

        return create_event_sink_args_type_2
