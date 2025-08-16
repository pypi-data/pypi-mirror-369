from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.webhook_type import WebhookType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.webhook_configuration_headers import WebhookConfigurationHeaders


T = TypeVar("T", bound="WebhookConfiguration")


@_attrs_define
class WebhookConfiguration:
    """Represents configuration to send messages to a webhook.

    Attributes:
        url (str): The URL for the webhook
        headers (Union[Unset, WebhookConfigurationHeaders]): Custom HTTP headers for the request
        webhook_type (Union[Unset, WebhookType]): Type of webhook. This is only used to differentiate between Torq
            webhooks and other webhooks right now. Default: WebhookType.OTHER.
    """

    url: str
    headers: Union[Unset, "WebhookConfigurationHeaders"] = UNSET
    webhook_type: Union[Unset, WebhookType] = WebhookType.OTHER
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        headers: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.headers, Unset):
            headers = self.headers.to_dict()

        webhook_type: Union[Unset, str] = UNSET
        if not isinstance(self.webhook_type, Unset):
            webhook_type = self.webhook_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
            }
        )
        if headers is not UNSET:
            field_dict["headers"] = headers
        if webhook_type is not UNSET:
            field_dict["webhook_type"] = webhook_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.webhook_configuration_headers import WebhookConfigurationHeaders

        d = src_dict.copy()
        url = d.pop("url")

        _headers = d.pop("headers", UNSET)
        headers: Union[Unset, WebhookConfigurationHeaders]
        if isinstance(_headers, Unset):
            headers = UNSET
        else:
            headers = WebhookConfigurationHeaders.from_dict(_headers)

        _webhook_type = d.pop("webhook_type", UNSET)
        webhook_type: Union[Unset, WebhookType]
        if isinstance(_webhook_type, Unset):
            webhook_type = UNSET
        else:
            webhook_type = WebhookType(_webhook_type)

        webhook_configuration = cls(
            url=url,
            headers=headers,
            webhook_type=webhook_type,
        )

        webhook_configuration.additional_properties = d
        return webhook_configuration

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
