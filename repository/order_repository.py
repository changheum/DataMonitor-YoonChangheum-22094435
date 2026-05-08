import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from domain.order import Order, OrderStatus


class OrderRepository(ABC):
    @abstractmethod
    def find_all(self) -> List[Order]:  # pragma: no cover
        pass


class JsonOrderRepository(OrderRepository):
    def __init__(self, file_path: Path):
        self._file_path = Path(file_path)

    def find_all(self) -> List[Order]:
        if not self._file_path.exists():
            return []
        data = json.loads(self._file_path.read_text(encoding="utf-8"))
        return [
            Order(
                order_id=d["order_id"],
                sample_id=d["sample_id"],
                customer=d["customer"],
                quantity=d["quantity"],
                status=OrderStatus[d["status"]],
            )
            for d in data
        ]
