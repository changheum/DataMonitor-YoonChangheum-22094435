from typing import Dict, List

from domain.order import Order, OrderStatus, MONITORED_STATUSES


class OrderMonitorService:
    def __init__(self, orders: List[Order]):
        self._orders = orders

    def get_order_counts(self) -> Dict[OrderStatus, int]:
        counts = {status: 0 for status in MONITORED_STATUSES}
        for order in self._orders:
            if order.status in counts:
                counts[order.status] += 1
        return counts
