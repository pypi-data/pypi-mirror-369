from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.detection_severity_type_0 import DetectionSeverityType0
from ..models.detection_severity_type_1 import DetectionSeverityType1
from ..models.detection_severity_type_2 import DetectionSeverityType2
from ..models.detection_severity_type_3 import DetectionSeverityType3
from ..models.detection_severity_type_4 import DetectionSeverityType4
from ..models.detection_severity_type_5 import DetectionSeverityType5
from ..models.detection_severity_type_6 import DetectionSeverityType6
from ..models.detection_severity_type_7 import DetectionSeverityType7
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.detection_alert_template import DetectionAlertTemplate


T = TypeVar("T", bound="UpdateDetectionRuleRequestData")


@_attrs_define
class UpdateDetectionRuleRequestData:
    """
    Attributes:
        id (UUID):
        alert_template (Union['DetectionAlertTemplate', None, Unset]): This implements a type which describes whether a
            value should be updated or not, that's used in most update routes in the API.

            This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
            Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

            Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
        debounce (Union[Unset, bool]): This implements a type which describes whether a value should be updated or not,
            that's used in most update routes in the API.

            This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
            Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

            Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
        description (Union[Unset, str]): This implements a type which describes whether a value should be updated or
            not, that's used in most update routes in the API.

            This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
            Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

            Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
        enabled (Union[Unset, bool]): This implements a type which describes whether a value should be updated or not,
            that's used in most update routes in the API.

            This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
            Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

            Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
        enabled_override (Union[None, Unset, bool]): This implements a type which describes whether a value should be
            updated or not, that's used in most update routes in the API.

            This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
            Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

            Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
        event_sink_ids (Union[Unset, list[UUID]]): This implements a type which describes whether a value should be
            updated or not, that's used in most update routes in the API.

            This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
            Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

            Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
        name (Union[Unset, str]): This implements a type which describes whether a value should be updated or not,
            that's used in most update routes in the API.

            This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
            Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

            Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
        query_text (Union[Unset, str]): This implements a type which describes whether a value should be updated or not,
            that's used in most update routes in the API.

            This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
            Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

            Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
        run_frequency_s (Union[Unset, int]): This implements a type which describes whether a value should be updated or
            not, that's used in most update routes in the API.

            This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
            Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

            Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
        severity (Union[DetectionSeverityType0, DetectionSeverityType1, DetectionSeverityType2, DetectionSeverityType3,
            DetectionSeverityType4, DetectionSeverityType5, DetectionSeverityType6, DetectionSeverityType7, Unset]): The
            severity of a detection rule. Uses the OCSF severity schema for detection findings. In particular, uses the
            integer and string representations of the severity levels as described in the OCSF schema spec here:
            <https://schema.ocsf.io/1.1.0/classes/detection_finding>
        sync_key (Union[None, Unset, str]): This implements a type which describes whether a value should be updated or
            not, that's used in most update routes in the API.

            This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
            Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

            Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
        tags (Union[None, Unset, list[str]]): This implements a type which describes whether a value should be updated
            or not, that's used in most update routes in the API.

            This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
            Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

            Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
        time_range_s (Union[Unset, int]): This implements a type which describes whether a value should be updated or
            not, that's used in most update routes in the API.

            This needs to implement Serialize for derive(JsonSchema) to work. It shouldn't ever need to be used in a
            Serialize context, as it's only Serialize in order to generate a JsonSchema properly.

            Please use with #[serde(default, deserialize_with=deserialize_update_value) in the struct.
    """

    id: UUID
    alert_template: Union["DetectionAlertTemplate", None, Unset] = UNSET
    debounce: Union[Unset, bool] = UNSET
    description: Union[Unset, str] = UNSET
    enabled: Union[Unset, bool] = UNSET
    enabled_override: Union[None, Unset, bool] = UNSET
    event_sink_ids: Union[Unset, list[UUID]] = UNSET
    name: Union[Unset, str] = UNSET
    query_text: Union[Unset, str] = UNSET
    run_frequency_s: Union[Unset, int] = UNSET
    severity: Union[
        DetectionSeverityType0,
        DetectionSeverityType1,
        DetectionSeverityType2,
        DetectionSeverityType3,
        DetectionSeverityType4,
        DetectionSeverityType5,
        DetectionSeverityType6,
        DetectionSeverityType7,
        Unset,
    ] = UNSET
    sync_key: Union[None, Unset, str] = UNSET
    tags: Union[None, Unset, list[str]] = UNSET
    time_range_s: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.detection_alert_template import DetectionAlertTemplate

        id = str(self.id)

        alert_template: Union[None, Unset, dict[str, Any]]
        if isinstance(self.alert_template, Unset):
            alert_template = UNSET
        elif isinstance(self.alert_template, DetectionAlertTemplate):
            alert_template = self.alert_template.to_dict()
        else:
            alert_template = self.alert_template

        debounce: Union[Unset, bool]
        if isinstance(self.debounce, Unset):
            debounce = UNSET
        else:
            debounce = self.debounce

        description: Union[Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        enabled: Union[Unset, bool]
        if isinstance(self.enabled, Unset):
            enabled = UNSET
        else:
            enabled = self.enabled

        enabled_override: Union[None, Unset, bool]
        if isinstance(self.enabled_override, Unset):
            enabled_override = UNSET
        else:
            enabled_override = self.enabled_override

        event_sink_ids: Union[Unset, list[str]]
        if isinstance(self.event_sink_ids, Unset):
            event_sink_ids = UNSET
        else:
            event_sink_ids = []
            for componentsschemas_update_value_for_array_of_event_sink_id_type_0_item_data in self.event_sink_ids:
                componentsschemas_update_value_for_array_of_event_sink_id_type_0_item = str(
                    componentsschemas_update_value_for_array_of_event_sink_id_type_0_item_data
                )
                event_sink_ids.append(componentsschemas_update_value_for_array_of_event_sink_id_type_0_item)

        name: Union[Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        query_text: Union[Unset, str]
        if isinstance(self.query_text, Unset):
            query_text = UNSET
        else:
            query_text = self.query_text

        run_frequency_s: Union[Unset, int]
        if isinstance(self.run_frequency_s, Unset):
            run_frequency_s = UNSET
        else:
            run_frequency_s = self.run_frequency_s

        severity: Union[Unset, str]
        if isinstance(self.severity, Unset):
            severity = UNSET
        elif isinstance(self.severity, DetectionSeverityType0):
            severity = self.severity.value
        elif isinstance(self.severity, DetectionSeverityType1):
            severity = self.severity.value
        elif isinstance(self.severity, DetectionSeverityType2):
            severity = self.severity.value
        elif isinstance(self.severity, DetectionSeverityType3):
            severity = self.severity.value
        elif isinstance(self.severity, DetectionSeverityType4):
            severity = self.severity.value
        elif isinstance(self.severity, DetectionSeverityType5):
            severity = self.severity.value
        elif isinstance(self.severity, DetectionSeverityType6):
            severity = self.severity.value
        else:
            severity = self.severity.value

        sync_key: Union[None, Unset, str]
        if isinstance(self.sync_key, Unset):
            sync_key = UNSET
        else:
            sync_key = self.sync_key

        tags: Union[None, Unset, list[str]]
        if isinstance(self.tags, Unset):
            tags = UNSET
        elif isinstance(self.tags, list):
            tags = self.tags

        else:
            tags = self.tags

        time_range_s: Union[Unset, int]
        if isinstance(self.time_range_s, Unset):
            time_range_s = UNSET
        else:
            time_range_s = self.time_range_s

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if alert_template is not UNSET:
            field_dict["alert_template"] = alert_template
        if debounce is not UNSET:
            field_dict["debounce"] = debounce
        if description is not UNSET:
            field_dict["description"] = description
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if enabled_override is not UNSET:
            field_dict["enabled_override"] = enabled_override
        if event_sink_ids is not UNSET:
            field_dict["event_sink_ids"] = event_sink_ids
        if name is not UNSET:
            field_dict["name"] = name
        if query_text is not UNSET:
            field_dict["query_text"] = query_text
        if run_frequency_s is not UNSET:
            field_dict["run_frequency_s"] = run_frequency_s
        if severity is not UNSET:
            field_dict["severity"] = severity
        if sync_key is not UNSET:
            field_dict["sync_key"] = sync_key
        if tags is not UNSET:
            field_dict["tags"] = tags
        if time_range_s is not UNSET:
            field_dict["time_range_s"] = time_range_s

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.detection_alert_template import DetectionAlertTemplate

        d = src_dict.copy()
        id = UUID(d.pop("id"))

        def _parse_alert_template(data: object) -> Union["DetectionAlertTemplate", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_update_value_for_nullable_detection_alert_template_type_0_type_1 = (
                    DetectionAlertTemplate.from_dict(data)
                )

                return componentsschemas_update_value_for_nullable_detection_alert_template_type_0_type_1
            except:  # noqa: E722
                pass
            return cast(Union["DetectionAlertTemplate", None, Unset], data)

        alert_template = _parse_alert_template(d.pop("alert_template", UNSET))

        def _parse_debounce(data: object) -> Union[Unset, bool]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, bool], data)

        debounce = _parse_debounce(d.pop("debounce", UNSET))

        def _parse_description(data: object) -> Union[Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_enabled(data: object) -> Union[Unset, bool]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, bool], data)

        enabled = _parse_enabled(d.pop("enabled", UNSET))

        def _parse_enabled_override(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        enabled_override = _parse_enabled_override(d.pop("enabled_override", UNSET))

        def _parse_event_sink_ids(data: object) -> Union[Unset, list[UUID]]:
            if isinstance(data, Unset):
                return data
            if not isinstance(data, list):
                raise TypeError()
            componentsschemas_update_value_for_array_of_event_sink_id_type_0 = []
            _componentsschemas_update_value_for_array_of_event_sink_id_type_0 = data
            for (
                componentsschemas_update_value_for_array_of_event_sink_id_type_0_item_data
            ) in _componentsschemas_update_value_for_array_of_event_sink_id_type_0:
                componentsschemas_update_value_for_array_of_event_sink_id_type_0_item = UUID(
                    componentsschemas_update_value_for_array_of_event_sink_id_type_0_item_data
                )

                componentsschemas_update_value_for_array_of_event_sink_id_type_0.append(
                    componentsschemas_update_value_for_array_of_event_sink_id_type_0_item
                )

            return componentsschemas_update_value_for_array_of_event_sink_id_type_0

        event_sink_ids = _parse_event_sink_ids(d.pop("event_sink_ids", UNSET))

        def _parse_name(data: object) -> Union[Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_query_text(data: object) -> Union[Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, str], data)

        query_text = _parse_query_text(d.pop("query_text", UNSET))

        def _parse_run_frequency_s(data: object) -> Union[Unset, int]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, int], data)

        run_frequency_s = _parse_run_frequency_s(d.pop("run_frequency_s", UNSET))

        def _parse_severity(
            data: object,
        ) -> Union[
            DetectionSeverityType0,
            DetectionSeverityType1,
            DetectionSeverityType2,
            DetectionSeverityType3,
            DetectionSeverityType4,
            DetectionSeverityType5,
            DetectionSeverityType6,
            DetectionSeverityType7,
            Unset,
        ]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_detection_severity_type_0 = DetectionSeverityType0(data)

                return componentsschemas_detection_severity_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_detection_severity_type_1 = DetectionSeverityType1(data)

                return componentsschemas_detection_severity_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_detection_severity_type_2 = DetectionSeverityType2(data)

                return componentsschemas_detection_severity_type_2
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_detection_severity_type_3 = DetectionSeverityType3(data)

                return componentsschemas_detection_severity_type_3
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_detection_severity_type_4 = DetectionSeverityType4(data)

                return componentsschemas_detection_severity_type_4
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_detection_severity_type_5 = DetectionSeverityType5(data)

                return componentsschemas_detection_severity_type_5
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_detection_severity_type_6 = DetectionSeverityType6(data)

                return componentsschemas_detection_severity_type_6
            except:  # noqa: E722
                pass
            if not isinstance(data, str):
                raise TypeError()
            componentsschemas_detection_severity_type_7 = DetectionSeverityType7(data)

            return componentsschemas_detection_severity_type_7

        severity = _parse_severity(d.pop("severity", UNSET))

        def _parse_sync_key(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        sync_key = _parse_sync_key(d.pop("sync_key", UNSET))

        def _parse_tags(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                componentsschemas_update_value_for_nullable_array_of_string_type_0_type_0 = cast(list[str], data)

                return componentsschemas_update_value_for_nullable_array_of_string_type_0_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        tags = _parse_tags(d.pop("tags", UNSET))

        def _parse_time_range_s(data: object) -> Union[Unset, int]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, int], data)

        time_range_s = _parse_time_range_s(d.pop("time_range_s", UNSET))

        update_detection_rule_request_data = cls(
            id=id,
            alert_template=alert_template,
            debounce=debounce,
            description=description,
            enabled=enabled,
            enabled_override=enabled_override,
            event_sink_ids=event_sink_ids,
            name=name,
            query_text=query_text,
            run_frequency_s=run_frequency_s,
            severity=severity,
            sync_key=sync_key,
            tags=tags,
            time_range_s=time_range_s,
        )

        update_detection_rule_request_data.additional_properties = d
        return update_detection_rule_request_data

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
