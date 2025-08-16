from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.tines_configuration import TinesConfiguration


T = TypeVar("T", bound="EventSinkConfigurationType2")


@_attrs_define
class EventSinkConfigurationType2:
    """
    Attributes:
        tines (TinesConfiguration):
    """

    tines: "TinesConfiguration"

    def to_dict(self) -> dict[str, Any]:
        tines = self.tines.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "Tines": tines,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.tines_configuration import TinesConfiguration

        d = src_dict.copy()
        tines = TinesConfiguration.from_dict(d.pop("Tines"))

        event_sink_configuration_type_2 = cls(
            tines=tines,
        )

        return event_sink_configuration_type_2
