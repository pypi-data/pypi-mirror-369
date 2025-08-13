from enum import Enum


class AvailabilityStatus(str, Enum):
    BACKORDER = "BackOrder"
    DISCONTINUED = "Discontinued"
    INSTOCK = "InStock"
    LIMITEDAVAILABILITY = "LimitedAvailability"
    OUTOFSTOCK = "OutOfStock"
    PREORDER = "PreOrder"
    SOLDOUT = "SoldOut"
    UNKNOWN = "Unknown"

    def __str__(self) -> str:
        return str(self.value)
