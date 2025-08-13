from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_config import SearchConfig
    from ..models.search_filters import SearchFilters


T = TypeVar("T", bound="SearchRequest")


@_attrs_define
class SearchRequest:
    """
    Attributes:
        query (Union[None, Unset, str]):
        image_url (Union[None, Unset, str]):
        base64_image (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):  Default: 20.
        filters (Union[Unset, SearchFilters]):
        config (Union[Unset, SearchConfig]): Configuration for a search request
        context (Union[None, Unset, str]): Context for the search
    """

    query: Union[None, Unset, str] = UNSET
    image_url: Union[None, Unset, str] = UNSET
    base64_image: Union[None, Unset, str] = UNSET
    limit: Union[None, Unset, int] = 20
    filters: Union[Unset, "SearchFilters"] = UNSET
    config: Union[Unset, "SearchConfig"] = UNSET
    context: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query: Union[None, Unset, str]
        if isinstance(self.query, Unset):
            query = UNSET
        else:
            query = self.query

        image_url: Union[None, Unset, str]
        if isinstance(self.image_url, Unset):
            image_url = UNSET
        else:
            image_url = self.image_url

        base64_image: Union[None, Unset, str]
        if isinstance(self.base64_image, Unset):
            base64_image = UNSET
        else:
            base64_image = self.base64_image

        limit: Union[None, Unset, int]
        if isinstance(self.limit, Unset):
            limit = UNSET
        else:
            limit = self.limit

        filters: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters.to_dict()

        config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        context: Union[None, Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET
        else:
            context = self.context

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if query is not UNSET:
            field_dict["query"] = query
        if image_url is not UNSET:
            field_dict["image_url"] = image_url
        if base64_image is not UNSET:
            field_dict["base64_image"] = base64_image
        if limit is not UNSET:
            field_dict["limit"] = limit
        if filters is not UNSET:
            field_dict["filters"] = filters
        if config is not UNSET:
            field_dict["config"] = config
        if context is not UNSET:
            field_dict["context"] = context

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.search_config import SearchConfig
        from ..models.search_filters import SearchFilters

        d = dict(src_dict)

        def _parse_query(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        query = _parse_query(d.pop("query", UNSET))

        def _parse_image_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        image_url = _parse_image_url(d.pop("image_url", UNSET))

        def _parse_base64_image(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        base64_image = _parse_base64_image(d.pop("base64_image", UNSET))

        def _parse_limit(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        limit = _parse_limit(d.pop("limit", UNSET))

        _filters = d.pop("filters", UNSET)
        filters: Union[Unset, SearchFilters]
        if isinstance(_filters, Unset):
            filters = UNSET
        else:
            filters = SearchFilters.from_dict(_filters)

        _config = d.pop("config", UNSET)
        config: Union[Unset, SearchConfig]
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = SearchConfig.from_dict(_config)

        def _parse_context(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        context = _parse_context(d.pop("context", UNSET))

        search_request = cls(
            query=query,
            image_url=image_url,
            base64_image=base64_image,
            limit=limit,
            filters=filters,
            config=config,
            context=context,
        )

        search_request.additional_properties = d
        return search_request

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
