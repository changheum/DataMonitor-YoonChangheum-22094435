from typing import Dict, List

from domain.order import Order, OrderStatus

_MONITORED_STATUSES = [
    OrderStatus.RESERVED,
    OrderStatus.PRODUCING,
    OrderStatus.CONFIRMED,
    OrderStatus.RELEASE,
]


class OrderMonitorService:
    def __init__(self, orders: List[Order]):
        self._orders = orders

    def get_order_counts(self) -> Dict[OrderStatus, int]:
        counts = {status: 0 for status in _MONITORED_STATUSES}
        for order in self._orders:
            if order.status in counts:
                counts[order.status] += 1
        return counts
