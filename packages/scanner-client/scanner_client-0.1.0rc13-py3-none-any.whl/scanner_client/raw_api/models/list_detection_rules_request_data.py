from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.detection_rule_sort_order import DetectionRuleSortOrder
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pagination_parameters import PaginationParameters


T = TypeVar("T", bound="ListDetectionRulesRequestData")


@_attrs_define
class ListDetectionRulesRequestData:
    """
    Attributes:
        tenant_id (UUID):
        pagination (Union['PaginationParameters', None, Unset]):
        sort_order (Union[DetectionRuleSortOrder, None, Unset]):
    """

    tenant_id: UUID
    pagination: Union["PaginationParameters", None, Unset] = UNSET
    sort_order: Union[DetectionRuleSortOrder, None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.pagination_parameters import PaginationParameters

        tenant_id = str(self.tenant_id)

        pagination: Union[None, Unset, dict[str, Any]]
        if isinstance(self.pagination, Unset):
            pagination = UNSET
        elif isinstance(self.pagination, PaginationParameters):
            pagination = self.pagination.to_dict()
        else:
            pagination = self.pagination

        sort_order: Union[None, Unset, str]
        if isinstance(self.sort_order, Unset):
            sort_order = UNSET
        elif isinstance(self.sort_order, DetectionRuleSortOrder):
            sort_order = self.sort_order.value
        else:
            sort_order = self.sort_order

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tenant_id": tenant_id,
            }
        )
        if pagination is not UNSET:
            field_dict["pagination"] = pagination
        if sort_order is not UNSET:
            field_dict["sort_order"] = sort_order

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.pagination_parameters import PaginationParameters

        d = src_dict.copy()
        tenant_id = UUID(d.pop("tenant_id"))

        def _parse_pagination(data: object) -> Union["PaginationParameters", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                pagination_type_1 = PaginationParameters.from_dict(data)

                return pagination_type_1
            except:  # noqa: E722
                pass
            return cast(Union["PaginationParameters", None, Unset], data)

        pagination = _parse_pagination(d.pop("pagination", UNSET))

        def _parse_sort_order(data: object) -> Union[DetectionRuleSortOrder, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                sort_order_type_1 = DetectionRuleSortOrder(data)

                return sort_order_type_1
            except:  # noqa: E722
                pass
            return cast(Union[DetectionRuleSortOrder, None, Unset], data)

        sort_order = _parse_sort_order(d.pop("sort_order", UNSET))

        list_detection_rules_request_data = cls(
            tenant_id=tenant_id,
            pagination=pagination,
            sort_order=sort_order,
        )

        list_detection_rules_request_data.additional_properties = d
        return list_detection_rules_request_data

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
