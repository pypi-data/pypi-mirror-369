from typing import TYPE_CHECKING, Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.create_event_sink_args_type_0 import CreateEventSinkArgsType0
    from ..models.create_event_sink_args_type_1 import CreateEventSinkArgsType1
    from ..models.create_event_sink_args_type_2 import CreateEventSinkArgsType2


T = TypeVar("T", bound="CreateEventSinkRequestData")


@_attrs_define
class CreateEventSinkRequestData:
    """
    Attributes:
        description (str):
        event_sink_args (Union['CreateEventSinkArgsType0', 'CreateEventSinkArgsType1', 'CreateEventSinkArgsType2']):
        name (str):
        tenant_id (UUID):
    """

    description: str
    event_sink_args: Union["CreateEventSinkArgsType0", "CreateEventSinkArgsType1", "CreateEventSinkArgsType2"]
    name: str
    tenant_id: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.create_event_sink_args_type_0 import CreateEventSinkArgsType0
        from ..models.create_event_sink_args_type_1 import CreateEventSinkArgsType1

        description = self.description

        event_sink_args: dict[str, Any]
        if isinstance(self.event_sink_args, CreateEventSinkArgsType0):
            event_sink_args = self.event_sink_args.to_dict()
        elif isinstance(self.event_sink_args, CreateEventSinkArgsType1):
            event_sink_args = self.event_sink_args.to_dict()
        else:
            event_sink_args = self.event_sink_args.to_dict()

        name = self.name

        tenant_id = str(self.tenant_id)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "event_sink_args": event_sink_args,
                "name": name,
                "tenant_id": tenant_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_event_sink_args_type_0 import CreateEventSinkArgsType0
        from ..models.create_event_sink_args_type_1 import CreateEventSinkArgsType1
        from ..models.create_event_sink_args_type_2 import CreateEventSinkArgsType2

        d = src_dict.copy()
        description = d.pop("description")

        def _parse_event_sink_args(
            data: object,
        ) -> Union["CreateEventSinkArgsType0", "CreateEventSinkArgsType1", "CreateEventSinkArgsType2"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_create_event_sink_args_type_0 = CreateEventSinkArgsType0.from_dict(data)

                return componentsschemas_create_event_sink_args_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_create_event_sink_args_type_1 = CreateEventSinkArgsType1.from_dict(data)

                return componentsschemas_create_event_sink_args_type_1
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_create_event_sink_args_type_2 = CreateEventSinkArgsType2.from_dict(data)

            return componentsschemas_create_event_sink_args_type_2

        event_sink_args = _parse_event_sink_args(d.pop("event_sink_args"))

        name = d.pop("name")

        tenant_id = UUID(d.pop("tenant_id"))

        create_event_sink_request_data = cls(
            description=description,
            event_sink_args=event_sink_args,
            name=name,
            tenant_id=tenant_id,
        )

        create_event_sink_request_data.additional_properties = d
        return create_event_sink_request_data

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
