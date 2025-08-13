from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Price")


@_attrs_define
class Price:
    """
    Attributes:
        price (float): The current price of the product, including any discounts.
        currency (str): The currency code of the product.
        compare_at_price (Union[None, Unset, float]): The original price of the product before any discounts.
    """

    price: float
    currency: str
    compare_at_price: Union[None, Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        price = self.price

        currency = self.currency

        compare_at_price: Union[None, Unset, float]
        if isinstance(self.compare_at_price, Unset):
            compare_at_price = UNSET
        else:
            compare_at_price = self.compare_at_price

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "price": price,
                "currency": currency,
            }
        )
        if compare_at_price is not UNSET:
            field_dict["compare_at_price"] = compare_at_price

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        price = d.pop("price")

        currency = d.pop("currency")

        def _parse_compare_at_price(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        compare_at_price = _parse_compare_at_price(d.pop("compare_at_price", UNSET))

        price = cls(
            price=price,
            currency=currency,
            compare_at_price=compare_at_price,
        )

        price.additional_properties = d
        return price

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
