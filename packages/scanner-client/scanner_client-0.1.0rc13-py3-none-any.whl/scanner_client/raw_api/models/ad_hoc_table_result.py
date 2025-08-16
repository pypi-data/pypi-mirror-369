from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.table_ui_state_type import TableUiStateType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ad_hoc_row_item import AdHocRowItem
    from ..models.ad_hoc_table_result_column_tags import AdHocTableResultColumnTags


T = TypeVar("T", bound="AdHocTableResult")


@_attrs_define
class AdHocTableResult:
    """
    Attributes:
        column_ordering (list[str]):
        column_tags (AdHocTableResultColumnTags):
        rows (list['AdHocRowItem']):
        table_type (Union[None, TableUiStateType, Unset]):
    """

    column_ordering: list[str]
    column_tags: "AdHocTableResultColumnTags"
    rows: list["AdHocRowItem"]
    table_type: Union[None, TableUiStateType, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        column_ordering = self.column_ordering

        column_tags = self.column_tags.to_dict()

        rows = []
        for rows_item_data in self.rows:
            rows_item = rows_item_data.to_dict()
            rows.append(rows_item)

        table_type: Union[None, Unset, str]
        if isinstance(self.table_type, Unset):
            table_type = UNSET
        elif isinstance(self.table_type, TableUiStateType):
            table_type = self.table_type.value
        else:
            table_type = self.table_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "column_ordering": column_ordering,
                "column_tags": column_tags,
                "rows": rows,
            }
        )
        if table_type is not UNSET:
            field_dict["table_type"] = table_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.ad_hoc_row_item import AdHocRowItem
        from ..models.ad_hoc_table_result_column_tags import AdHocTableResultColumnTags

        d = src_dict.copy()
        column_ordering = cast(list[str], d.pop("column_ordering"))

        column_tags = AdHocTableResultColumnTags.from_dict(d.pop("column_tags"))

        rows = []
        _rows = d.pop("rows")
        for rows_item_data in _rows:
            rows_item = AdHocRowItem.from_dict(rows_item_data)

            rows.append(rows_item)

        def _parse_table_type(data: object) -> Union[None, TableUiStateType, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                table_type_type_1 = TableUiStateType(data)

                return table_type_type_1
            except:  # noqa: E722
                pass
            return cast(Union[None, TableUiStateType, Unset], data)

        table_type = _parse_table_type(d.pop("table_type", UNSET))

        ad_hoc_table_result = cls(
            column_ordering=column_ordering,
            column_tags=column_tags,
            rows=rows,
            table_type=table_type,
        )

        ad_hoc_table_result.additional_properties = d
        return ad_hoc_table_result

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
