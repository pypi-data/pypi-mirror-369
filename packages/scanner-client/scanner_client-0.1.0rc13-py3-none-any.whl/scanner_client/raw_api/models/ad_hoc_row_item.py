from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.ad_hoc_row_item_columns import AdHocRowItemColumns
    from ..models.log_event_id import LogEventId


T = TypeVar("T", bound="AdHocRowItem")


@_attrs_define
class AdHocRowItem:
    """
    Attributes:
        columns (AdHocRowItemColumns):
        row_id (Union['LogEventId', int]):
    """

    columns: "AdHocRowItemColumns"
    row_id: Union["LogEventId", int]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.log_event_id import LogEventId

        columns = self.columns.to_dict()

        row_id: Union[dict[str, Any], int]
        if isinstance(self.row_id, LogEventId):
            row_id = self.row_id.to_dict()
        else:
            row_id = self.row_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "columns": columns,
                "row_id": row_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.ad_hoc_row_item_columns import AdHocRowItemColumns
        from ..models.log_event_id import LogEventId

        d = src_dict.copy()
        columns = AdHocRowItemColumns.from_dict(d.pop("columns"))

        def _parse_row_id(data: object) -> Union["LogEventId", int]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_any_row_id_json_type_0 = LogEventId.from_dict(data)

                return componentsschemas_any_row_id_json_type_0
            except:  # noqa: E722
                pass
            return cast(Union["LogEventId", int], data)

        row_id = _parse_row_id(d.pop("row_id"))

        ad_hoc_row_item = cls(
            columns=columns,
            row_id=row_id,
        )

        ad_hoc_row_item.additional_properties = d
        return ad_hoc_row_item

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
