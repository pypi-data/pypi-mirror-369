from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ad_hoc_query_progress_metadata import AdHocQueryProgressMetadata
    from ..models.ad_hoc_table_result import AdHocTableResult


T = TypeVar("T", bound="AdHocQueryProgressResponse")


@_attrs_define
class AdHocQueryProgressResponse:
    """
    Attributes:
        is_completed (bool):
        metadata (AdHocQueryProgressMetadata):
        results (Union['AdHocTableResult', None, Unset]):
    """

    is_completed: bool
    metadata: "AdHocQueryProgressMetadata"
    results: Union["AdHocTableResult", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.ad_hoc_table_result import AdHocTableResult

        is_completed = self.is_completed

        metadata = self.metadata.to_dict()

        results: Union[None, Unset, dict[str, Any]]
        if isinstance(self.results, Unset):
            results = UNSET
        elif isinstance(self.results, AdHocTableResult):
            results = self.results.to_dict()
        else:
            results = self.results

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "is_completed": is_completed,
                "metadata": metadata,
            }
        )
        if results is not UNSET:
            field_dict["results"] = results

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.ad_hoc_query_progress_metadata import AdHocQueryProgressMetadata
        from ..models.ad_hoc_table_result import AdHocTableResult

        d = src_dict.copy()
        is_completed = d.pop("is_completed")

        metadata = AdHocQueryProgressMetadata.from_dict(d.pop("metadata"))

        def _parse_results(data: object) -> Union["AdHocTableResult", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                results_type_1 = AdHocTableResult.from_dict(data)

                return results_type_1
            except:  # noqa: E722
                pass
            return cast(Union["AdHocTableResult", None, Unset], data)

        results = _parse_results(d.pop("results", UNSET))

        ad_hoc_query_progress_response = cls(
            is_completed=is_completed,
            metadata=metadata,
            results=results,
        )

        ad_hoc_query_progress_response.additional_properties = d
        return ad_hoc_query_progress_response

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
