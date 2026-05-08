import sys
from typing import Dict, List, TextIO

from domain.order import OrderStatus
from service.inventory_monitor_service import InventoryStatus

_ORDER_SECTION = "=== 주문 현황 ==="
_INVENTORY_SECTION = "=== 재고 현황 ==="
_MONITORED_STATUSES = [
    OrderStatus.RESERVED,
    OrderStatus.PRODUCING,
    OrderStatus.CONFIRMED,
    OrderStatus.RELEASE,
]


class MonitorDisplay:
    def __init__(self, output: TextIO = None):
        self.output = output if output is not None else sys.stdout

    def render(self, order_counts: Dict[OrderStatus, int], inventory_status: List[dict]) -> None:
        self._render_order_section(order_counts)
        self._render_inventory_section(inventory_status)

    def _render_order_section(self, counts: Dict[OrderStatus, int]) -> None:
        print(_ORDER_SECTION, file=self.output)
        print(f"  {'상태':<12} {'건수':>4}", file=self.output)
        print(f"  {'-'*18}", file=self.output)
        for status in _MONITORED_STATUSES:
            print(f"  {status.name:<12} {counts.get(status, 0):>4}", file=self.output)
        print(file=self.output)

    def _render_inventory_section(self, inventory_status: List[dict]) -> None:
        print(_INVENTORY_SECTION, file=self.output)
        if not inventory_status:
            print("  등록된 시료 없음", file=self.output)
            return
        print(f"  {'시료명':<12} {'재고':>6}  {'상태'}", file=self.output)
        print(f"  {'-'*26}", file=self.output)
        for entry in inventory_status:
            label = entry["status"].value
            print(f"  {entry['name']:<12} {entry['stock']:>6}  {label}", file=self.output)
        print(file=self.output)
