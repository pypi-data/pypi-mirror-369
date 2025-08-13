from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchFilterPrice")


@_attrs_define
class SearchFilterPrice:
    """Price filter. Values are inclusive.

    Attributes:
        min_price (Union[None, Unset, float]): Minimum price, in dollars and cents
        max_price (Union[None, Unset, float]): Maximum price, in dollars and cents
    """

    min_price: Union[None, Unset, float] = UNSET
    max_price: Union[None, Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        min_price: Union[None, Unset, float]
        if isinstance(self.min_price, Unset):
            min_price = UNSET
        else:
            min_price = self.min_price

        max_price: Union[None, Unset, float]
        if isinstance(self.max_price, Unset):
            max_price = UNSET
        else:
            max_price = self.max_price

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if min_price is not UNSET:
            field_dict["min_price"] = min_price
        if max_price is not UNSET:
            field_dict["max_price"] = max_price

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_min_price(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        min_price = _parse_min_price(d.pop("min_price", UNSET))

        def _parse_max_price(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        max_price = _parse_max_price(d.pop("max_price", UNSET))

        search_filter_price = cls(
            min_price=min_price,
            max_price=max_price,
        )

        search_filter_price.additional_properties = d
        return search_filter_price

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
