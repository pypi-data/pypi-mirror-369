from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.availability_status import AvailabilityStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.price import Price
    from ..models.variant import Variant


T = TypeVar("T", bound="Product")


@_attrs_define
class Product:
    """A product

    Attributes:
        id (str):
        score (float):
        url (str):
        title (str):
        brand_name (str):
        image_url (str):
        price (Price):
        availability (AvailabilityStatus):
        description (Union[None, Unset, str]):
        variants (Union[Unset, list['Variant']]):
    """

    id: str
    score: float
    url: str
    title: str
    brand_name: str
    image_url: str
    price: "Price"
    availability: AvailabilityStatus
    description: Union[None, Unset, str] = UNSET
    variants: Union[Unset, list["Variant"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        score = self.score

        url = self.url

        title = self.title

        brand_name = self.brand_name

        image_url = self.image_url

        price = self.price.to_dict()

        availability = self.availability.value

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        variants: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.variants, Unset):
            variants = []
            for variants_item_data in self.variants:
                variants_item = variants_item_data.to_dict()
                variants.append(variants_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "score": score,
                "url": url,
                "title": title,
                "brand_name": brand_name,
                "image_url": image_url,
                "price": price,
                "availability": availability,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if variants is not UNSET:
            field_dict["variants"] = variants

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.price import Price
        from ..models.variant import Variant

        d = dict(src_dict)
        id = d.pop("id")

        score = d.pop("score")

        url = d.pop("url")

        title = d.pop("title")

        brand_name = d.pop("brand_name")

        image_url = d.pop("image_url")

        price = Price.from_dict(d.pop("price"))

        availability = AvailabilityStatus(d.pop("availability"))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        variants = []
        _variants = d.pop("variants", UNSET)
        for variants_item_data in _variants or []:
            variants_item = Variant.from_dict(variants_item_data)

            variants.append(variants_item)

        product = cls(
            id=id,
            score=score,
            url=url,
            title=title,
            brand_name=brand_name,
            image_url=image_url,
            price=price,
            availability=availability,
            description=description,
            variants=variants,
        )

        product.additional_properties = d
        return product

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
