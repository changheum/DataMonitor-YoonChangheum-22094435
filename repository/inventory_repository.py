import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from domain.inventory import InventoryItem


class InventoryRepository(ABC):
    @abstractmethod
    def find_all(self) -> List[InventoryItem]:  # pragma: no cover
        pass

    @abstractmethod
    def find_by_sample_id(self, sample_id: str) -> Optional[InventoryItem]:  # pragma: no cover
        pass


class JsonInventoryRepository(InventoryRepository):
    def __init__(self, file_path: Path):
        self._file_path = Path(file_path)

    def find_all(self) -> List[InventoryItem]:
        if not self._file_path.exists():
            return []
        data = json.loads(self._file_path.read_text(encoding="utf-8"))
        return [
            InventoryItem(
                sample_id=d["sample_id"],
                stock_quantity=d["stock_quantity"],
            )
            for d in data
        ]

    def find_by_sample_id(self, sample_id: str) -> Optional[InventoryItem]:
        return next((i for i in self.find_all() if i.sample_id == sample_id), None)
