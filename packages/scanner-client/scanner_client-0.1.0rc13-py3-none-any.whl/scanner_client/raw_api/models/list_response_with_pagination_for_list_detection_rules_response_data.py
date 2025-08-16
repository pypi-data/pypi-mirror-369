from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.list_detection_rules_response_data import ListDetectionRulesResponseData
    from ..models.pagination_metadata import PaginationMetadata


T = TypeVar("T", bound="ListResponseWithPaginationForListDetectionRulesResponseData")


@_attrs_define
class ListResponseWithPaginationForListDetectionRulesResponseData:
    """
    Attributes:
        data (ListDetectionRulesResponseData):
        pagination (Union['PaginationMetadata', None, Unset]):
    """

    data: "ListDetectionRulesResponseData"
    pagination: Union["PaginationMetadata", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.pagination_metadata import PaginationMetadata

        data = self.data.to_dict()

        pagination: Union[None, Unset, dict[str, Any]]
        if isinstance(self.pagination, Unset):
            pagination = UNSET
        elif isinstance(self.pagination, PaginationMetadata):
            pagination = self.pagination.to_dict()
        else:
            pagination = self.pagination

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )
        if pagination is not UNSET:
            field_dict["pagination"] = pagination

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.list_detection_rules_response_data import ListDetectionRulesResponseData
        from ..models.pagination_metadata import PaginationMetadata

        d = src_dict.copy()
        data = ListDetectionRulesResponseData.from_dict(d.pop("data"))

        def _parse_pagination(data: object) -> Union["PaginationMetadata", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                pagination_type_1 = PaginationMetadata.from_dict(data)

                return pagination_type_1
            except:  # noqa: E722
                pass
            return cast(Union["PaginationMetadata", None, Unset], data)

        pagination = _parse_pagination(d.pop("pagination", UNSET))

        list_response_with_pagination_for_list_detection_rules_response_data = cls(
            data=data,
            pagination=pagination,
        )

        list_response_with_pagination_for_list_detection_rules_response_data.additional_properties = d
        return list_response_with_pagination_for_list_detection_rules_response_data

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
