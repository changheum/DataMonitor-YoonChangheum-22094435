from dataclasses import dataclass
from enum import Enum


class OrderStatus(Enum):
    RESERVED = "RESERVED"
    REJECTED = "REJECTED"
    PRODUCING = "PRODUCING"
    CONFIRMED = "CONFIRMED"
    RELEASE = "RELEASE"


MONITORED_STATUSES = [
    OrderStatus.RESERVED,
    OrderStatus.PRODUCING,
    OrderStatus.CONFIRMED,
    OrderStatus.RELEASE,
]


@dataclass
class Order:
    order_id: str
    sample_id: str
    customer: str
    quantity: int
    status: OrderStatus

    def __post_init__(self):
        if not self.order_id:
            raise ValueError("order_id cannot be empty")
        if not self.sample_id:
            raise ValueError("sample_id cannot be empty")
        if not self.customer:
            raise ValueError("customer cannot be empty")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
