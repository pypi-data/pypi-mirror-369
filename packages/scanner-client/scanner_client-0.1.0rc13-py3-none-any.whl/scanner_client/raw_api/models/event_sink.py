import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.event_sink_type import EventSinkType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.event_sink_configuration_type_0 import EventSinkConfigurationType0
    from ..models.event_sink_configuration_type_1 import EventSinkConfigurationType1
    from ..models.event_sink_configuration_type_2 import EventSinkConfigurationType2
    from ..models.event_sink_configuration_type_3 import EventSinkConfigurationType3


T = TypeVar("T", bound="EventSink")


@_attrs_define
class EventSink:
    """
    Attributes:
        configuration (Union['EventSinkConfigurationType0', 'EventSinkConfigurationType1',
            'EventSinkConfigurationType2', 'EventSinkConfigurationType3']):
        created_at (datetime.datetime):
        description (str):
        event_sink_type (EventSinkType):
        id (UUID):
        name (str):
        tenant_id (UUID):
        updated_at (datetime.datetime):
        integration_id (Union[None, UUID, Unset]):
    """

    configuration: Union[
        "EventSinkConfigurationType0",
        "EventSinkConfigurationType1",
        "EventSinkConfigurationType2",
        "EventSinkConfigurationType3",
    ]
    created_at: datetime.datetime
    description: str
    event_sink_type: EventSinkType
    id: UUID
    name: str
    tenant_id: UUID
    updated_at: datetime.datetime
    integration_id: Union[None, UUID, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.event_sink_configuration_type_0 import EventSinkConfigurationType0
        from ..models.event_sink_configuration_type_1 import EventSinkConfigurationType1
        from ..models.event_sink_configuration_type_2 import EventSinkConfigurationType2

        configuration: dict[str, Any]
        if isinstance(self.configuration, EventSinkConfigurationType0):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, EventSinkConfigurationType1):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, EventSinkConfigurationType2):
            configuration = self.configuration.to_dict()
        else:
            configuration = self.configuration.to_dict()

        created_at = self.created_at.isoformat()

        description = self.description

        event_sink_type = self.event_sink_type.value

        id = str(self.id)

        name = self.name

        tenant_id = str(self.tenant_id)

        updated_at = self.updated_at.isoformat()

        integration_id: Union[None, Unset, str]
        if isinstance(self.integration_id, Unset):
            integration_id = UNSET
        elif isinstance(self.integration_id, UUID):
            integration_id = str(self.integration_id)
        else:
            integration_id = self.integration_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "configuration": configuration,
                "created_at": created_at,
                "description": description,
                "event_sink_type": event_sink_type,
                "id": id,
                "name": name,
                "tenant_id": tenant_id,
                "updated_at": updated_at,
            }
        )
        if integration_id is not UNSET:
            field_dict["integration_id"] = integration_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.event_sink_configuration_type_0 import EventSinkConfigurationType0
        from ..models.event_sink_configuration_type_1 import EventSinkConfigurationType1
        from ..models.event_sink_configuration_type_2 import EventSinkConfigurationType2
        from ..models.event_sink_configuration_type_3 import EventSinkConfigurationType3

        d = src_dict.copy()

        def _parse_configuration(
            data: object,
        ) -> Union[
            "EventSinkConfigurationType0",
            "EventSinkConfigurationType1",
            "EventSinkConfigurationType2",
            "EventSinkConfigurationType3",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_sink_configuration_type_0 = EventSinkConfigurationType0.from_dict(data)

                return componentsschemas_event_sink_configuration_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_sink_configuration_type_1 = EventSinkConfigurationType1.from_dict(data)

                return componentsschemas_event_sink_configuration_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_sink_configuration_type_2 = EventSinkConfigurationType2.from_dict(data)

                return componentsschemas_event_sink_configuration_type_2
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_event_sink_configuration_type_3 = EventSinkConfigurationType3.from_dict(data)

            return componentsschemas_event_sink_configuration_type_3

        configuration = _parse_configuration(d.pop("configuration"))

        created_at = isoparse(d.pop("created_at"))

        description = d.pop("description")

        event_sink_type = EventSinkType(d.pop("event_sink_type"))

        id = UUID(d.pop("id"))

        name = d.pop("name")

        tenant_id = UUID(d.pop("tenant_id"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_integration_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                integration_id_type_1 = UUID(data)

                return integration_id_type_1
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        integration_id = _parse_integration_id(d.pop("integration_id", UNSET))

        event_sink = cls(
            configuration=configuration,
            created_at=created_at,
            description=description,
            event_sink_type=event_sink_type,
            id=id,
            name=name,
            tenant_id=tenant_id,
            updated_at=updated_at,
            integration_id=integration_id,
        )

        event_sink.additional_properties = d
        return event_sink

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
