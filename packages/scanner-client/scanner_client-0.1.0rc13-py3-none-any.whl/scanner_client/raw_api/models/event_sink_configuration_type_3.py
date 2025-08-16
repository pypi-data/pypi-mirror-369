from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.webhook_configuration import WebhookConfiguration


T = TypeVar("T", bound="EventSinkConfigurationType3")


@_attrs_define
class EventSinkConfigurationType3:
    """
    Attributes:
        webhook (WebhookConfiguration): Represents configuration to send messages to a webhook.
    """

    webhook: "WebhookConfiguration"

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
        from ..models.webhook_configuration import WebhookConfiguration

        d = src_dict.copy()
        webhook = WebhookConfiguration.from_dict(d.pop("Webhook"))

        event_sink_configuration_type_3 = cls(
            webhook=webhook,
        )

        return event_sink_configuration_type_3
