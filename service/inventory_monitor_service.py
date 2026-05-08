from enum import Enum
from typing import Dict, List

from domain.inventory import InventoryItem
from domain.order import Order, OrderStatus
from domain.sample import Sample

_ACTIVE_STATUSES = {OrderStatus.RESERVED, OrderStatus.PRODUCING, OrderStatus.CONFIRMED}


class InventoryStatus(Enum):
    SUFFICIENT = "여유"
    INSUFFICIENT = "부족"
    DEPLETED = "고갈"


class InventoryMonitorService:
    def __init__(self, samples: List[Sample], inventory: List[InventoryItem], orders: List[Order]):
        self._samples = samples
        self._inventory = {item.sample_id: item for item in inventory}
        self._active_quantity = self._calc_active_quantity(orders)

    @staticmethod
    def _calc_active_quantity(orders: List[Order]) -> Dict[str, int]:
        totals: Dict[str, int] = {}
        for order in orders:
            if order.status in _ACTIVE_STATUSES:
                totals[order.sample_id] = totals.get(order.sample_id, 0) + order.quantity
        return totals

    def get_inventory_status(self) -> List[dict]:
        result = []
        for sample in self._samples:
            item = self._inventory.get(sample.sample_id)
            stock = item.stock_quantity if item else 0
            active_qty = self._active_quantity.get(sample.sample_id, 0)
            result.append({
                "sample_id": sample.sample_id,
                "name": sample.name,
                "stock": stock,
                "status": self._determine_status(stock, active_qty),
            })
        return result

    @staticmethod
    def _determine_status(stock: int, active_qty: int) -> InventoryStatus:
        if stock == 0:
            return InventoryStatus.DEPLETED
        if stock < active_qty:
            return InventoryStatus.INSUFFICIENT
        return InventoryStatus.SUFFICIENT
