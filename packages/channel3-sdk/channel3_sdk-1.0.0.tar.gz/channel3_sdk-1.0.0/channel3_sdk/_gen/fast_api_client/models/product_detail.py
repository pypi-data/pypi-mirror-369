from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.availability_status import AvailabilityStatus
from ..models.product_detail_gender_type_0 import ProductDetailGenderType0
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.price import Price
    from ..models.variant import Variant


T = TypeVar("T", bound="ProductDetail")


@_attrs_define
class ProductDetail:
    """A product with detailed information

    Attributes:
        id (str):
        url (str):
        title (str):
        price (Price):
        availability (AvailabilityStatus):
        description (Union[None, Unset, str]):
        brand_id (Union[None, Unset, str]):
        brand_name (Union[None, Unset, str]):
        image_urls (Union[None, Unset, list[str]]):
        gender (Union[None, ProductDetailGenderType0, Unset]):
        materials (Union[None, Unset, list[str]]):
        key_features (Union[None, Unset, list[str]]):
        variants (Union[Unset, list['Variant']]):
    """

    id: str
    url: str
    title: str
    price: "Price"
    availability: AvailabilityStatus
    description: Union[None, Unset, str] = UNSET
    brand_id: Union[None, Unset, str] = UNSET
    brand_name: Union[None, Unset, str] = UNSET
    image_urls: Union[None, Unset, list[str]] = UNSET
    gender: Union[None, ProductDetailGenderType0, Unset] = UNSET
    materials: Union[None, Unset, list[str]] = UNSET
    key_features: Union[None, Unset, list[str]] = UNSET
    variants: Union[Unset, list["Variant"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        url = self.url

        title = self.title

        price = self.price.to_dict()

        availability = self.availability.value

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        brand_id: Union[None, Unset, str]
        if isinstance(self.brand_id, Unset):
            brand_id = UNSET
        else:
            brand_id = self.brand_id

        brand_name: Union[None, Unset, str]
        if isinstance(self.brand_name, Unset):
            brand_name = UNSET
        else:
            brand_name = self.brand_name

        image_urls: Union[None, Unset, list[str]]
        if isinstance(self.image_urls, Unset):
            image_urls = UNSET
        elif isinstance(self.image_urls, list):
            image_urls = self.image_urls

        else:
            image_urls = self.image_urls

        gender: Union[None, Unset, str]
        if isinstance(self.gender, Unset):
            gender = UNSET
        elif isinstance(self.gender, ProductDetailGenderType0):
            gender = self.gender.value
        else:
            gender = self.gender

        materials: Union[None, Unset, list[str]]
        if isinstance(self.materials, Unset):
            materials = UNSET
        elif isinstance(self.materials, list):
            materials = self.materials

        else:
            materials = self.materials

        key_features: Union[None, Unset, list[str]]
        if isinstance(self.key_features, Unset):
            key_features = UNSET
        elif isinstance(self.key_features, list):
            key_features = self.key_features

        else:
            key_features = self.key_features

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
                "url": url,
                "title": title,
                "price": price,
                "availability": availability,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if brand_id is not UNSET:
            field_dict["brand_id"] = brand_id
        if brand_name is not UNSET:
            field_dict["brand_name"] = brand_name
        if image_urls is not UNSET:
            field_dict["image_urls"] = image_urls
        if gender is not UNSET:
            field_dict["gender"] = gender
        if materials is not UNSET:
            field_dict["materials"] = materials
        if key_features is not UNSET:
            field_dict["key_features"] = key_features
        if variants is not UNSET:
            field_dict["variants"] = variants

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.price import Price
        from ..models.variant import Variant

        d = dict(src_dict)
        id = d.pop("id")

        url = d.pop("url")

        title = d.pop("title")

        price = Price.from_dict(d.pop("price"))

        availability = AvailabilityStatus(d.pop("availability"))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_brand_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        brand_id = _parse_brand_id(d.pop("brand_id", UNSET))

        def _parse_brand_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        brand_name = _parse_brand_name(d.pop("brand_name", UNSET))

        def _parse_image_urls(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                image_urls_type_0 = cast(list[str], data)

                return image_urls_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        image_urls = _parse_image_urls(d.pop("image_urls", UNSET))

        def _parse_gender(data: object) -> Union[None, ProductDetailGenderType0, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                gender_type_0 = ProductDetailGenderType0(data)

                return gender_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, ProductDetailGenderType0, Unset], data)

        gender = _parse_gender(d.pop("gender", UNSET))

        def _parse_materials(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                materials_type_0 = cast(list[str], data)

                return materials_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        materials = _parse_materials(d.pop("materials", UNSET))

        def _parse_key_features(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                key_features_type_0 = cast(list[str], data)

                return key_features_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        key_features = _parse_key_features(d.pop("key_features", UNSET))

        variants = []
        _variants = d.pop("variants", UNSET)
        for variants_item_data in _variants or []:
            variants_item = Variant.from_dict(variants_item_data)

            variants.append(variants_item)

        product_detail = cls(
            id=id,
            url=url,
            title=title,
            price=price,
            availability=availability,
            description=description,
            brand_id=brand_id,
            brand_name=brand_name,
            image_urls=image_urls,
            gender=gender,
            materials=materials,
            key_features=key_features,
            variants=variants,
        )

        product_detail.additional_properties = d
        return product_detail

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
