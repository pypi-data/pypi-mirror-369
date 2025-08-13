from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchConfig")


@_attrs_define
class SearchConfig:
    """Configuration for a search request

    Attributes:
        enrich_query (Union[Unset, bool]):  Default: True.
        semantic_search (Union[Unset, bool]):  Default: True.
    """

    enrich_query: Union[Unset, bool] = True
    semantic_search: Union[Unset, bool] = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enrich_query = self.enrich_query

        semantic_search = self.semantic_search

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enrich_query is not UNSET:
            field_dict["enrich_query"] = enrich_query
        if semantic_search is not UNSET:
            field_dict["semantic_search"] = semantic_search

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enrich_query = d.pop("enrich_query", UNSET)

        semantic_search = d.pop("semantic_search", UNSET)

        search_config = cls(
            enrich_query=enrich_query,
            semantic_search=semantic_search,
        )

        search_config.additional_properties = d
        return search_config

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
