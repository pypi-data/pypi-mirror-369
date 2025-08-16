from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AdHocQueryProgressRequestData")


@_attrs_define
class AdHocQueryProgressRequestData:
    """
    Attributes:
        show_intermediate_results (Union[Unset, bool]):  Default: True.
    """

    show_intermediate_results: Union[Unset, bool] = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        show_intermediate_results = self.show_intermediate_results

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if show_intermediate_results is not UNSET:
            field_dict["show_intermediate_results"] = show_intermediate_results

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        show_intermediate_results = d.pop("show_intermediate_results", UNSET)

        ad_hoc_query_progress_request_data = cls(
            show_intermediate_results=show_intermediate_results,
        )

        ad_hoc_query_progress_request_data.additional_properties = d
        return ad_hoc_query_progress_request_data

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
