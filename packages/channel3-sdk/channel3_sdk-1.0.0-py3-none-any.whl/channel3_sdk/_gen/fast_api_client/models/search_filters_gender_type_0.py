from enum import Enum


class SearchFiltersGenderType0(str, Enum):
    FEMALE = "female"
    MALE = "male"
    UNISEX = "unisex"

    def __str__(self) -> str:
        return str(self.value)
