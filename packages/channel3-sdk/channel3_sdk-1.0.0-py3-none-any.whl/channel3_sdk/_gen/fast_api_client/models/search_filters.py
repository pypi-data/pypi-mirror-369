from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.availability_status import AvailabilityStatus
from ..models.search_filters_gender_type_0 import SearchFiltersGenderType0
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_filter_price import SearchFilterPrice


T = TypeVar("T", bound="SearchFilters")


@_attrs_define
class SearchFilters:
    """
    Attributes:
        brand_ids (Union[None, Unset, list[str]]): List of brand IDs
        gender (Union[None, SearchFiltersGenderType0, Unset]):
        price (Union['SearchFilterPrice', None, Unset]): Price filter. Values are inclusive.
        availability (Union[None, Unset, list[AvailabilityStatus]]): List of availability statuses
    """

    brand_ids: Union[None, Unset, list[str]] = UNSET
    gender: Union[None, SearchFiltersGenderType0, Unset] = UNSET
    price: Union["SearchFilterPrice", None, Unset] = UNSET
    availability: Union[None, Unset, list[AvailabilityStatus]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.search_filter_price import SearchFilterPrice

        brand_ids: Union[None, Unset, list[str]]
        if isinstance(self.brand_ids, Unset):
            brand_ids = UNSET
        elif isinstance(self.brand_ids, list):
            brand_ids = self.brand_ids

        else:
            brand_ids = self.brand_ids

        gender: Union[None, Unset, str]
        if isinstance(self.gender, Unset):
            gender = UNSET
        elif isinstance(self.gender, SearchFiltersGenderType0):
            gender = self.gender.value
        else:
            gender = self.gender

        price: Union[None, Unset, dict[str, Any]]
        if isinstance(self.price, Unset):
            price = UNSET
        elif isinstance(self.price, SearchFilterPrice):
            price = self.price.to_dict()
        else:
            price = self.price

        availability: Union[None, Unset, list[str]]
        if isinstance(self.availability, Unset):
            availability = UNSET
        elif isinstance(self.availability, list):
            availability = []
            for availability_type_0_item_data in self.availability:
                availability_type_0_item = availability_type_0_item_data.value
                availability.append(availability_type_0_item)

        else:
            availability = self.availability

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if brand_ids is not UNSET:
            field_dict["brand_ids"] = brand_ids
        if gender is not UNSET:
            field_dict["gender"] = gender
        if price is not UNSET:
            field_dict["price"] = price
        if availability is not UNSET:
            field_dict["availability"] = availability

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.search_filter_price import SearchFilterPrice

        d = dict(src_dict)

        def _parse_brand_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                brand_ids_type_0 = cast(list[str], data)

                return brand_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        brand_ids = _parse_brand_ids(d.pop("brand_ids", UNSET))

        def _parse_gender(data: object) -> Union[None, SearchFiltersGenderType0, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                gender_type_0 = SearchFiltersGenderType0(data)

                return gender_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, SearchFiltersGenderType0, Unset], data)

        gender = _parse_gender(d.pop("gender", UNSET))

        def _parse_price(data: object) -> Union["SearchFilterPrice", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                price_type_0 = SearchFilterPrice.from_dict(data)

                return price_type_0
            except:  # noqa: E722
                pass
            return cast(Union["SearchFilterPrice", None, Unset], data)

        price = _parse_price(d.pop("price", UNSET))

        def _parse_availability(data: object) -> Union[None, Unset, list[AvailabilityStatus]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                availability_type_0 = []
                _availability_type_0 = data
                for availability_type_0_item_data in _availability_type_0:
                    availability_type_0_item = AvailabilityStatus(availability_type_0_item_data)

                    availability_type_0.append(availability_type_0_item)

                return availability_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[AvailabilityStatus]], data)

        availability = _parse_availability(d.pop("availability", UNSET))

        search_filters = cls(
            brand_ids=brand_ids,
            gender=gender,
            price=price,
            availability=availability,
        )

        search_filters.additional_properties = d
        return search_filters

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
