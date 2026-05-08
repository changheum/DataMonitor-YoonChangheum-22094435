import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from domain.sample import Sample


class SampleRepository(ABC):
    @abstractmethod
    def find_all(self) -> List[Sample]:  # pragma: no cover
        pass

    @abstractmethod
    def find_by_id(self, sample_id: str) -> Optional[Sample]:  # pragma: no cover
        pass


class JsonSampleRepository(SampleRepository):
    def __init__(self, file_path: Path):
        self._file_path = Path(file_path)

    def find_all(self) -> List[Sample]:
        if not self._file_path.exists():
            return []
        data = json.loads(self._file_path.read_text(encoding="utf-8"))
        return [
            Sample(
                sample_id=d["sample_id"],
                name=d["name"],
                avg_production_time=d["avg_production_time"],
                yield_rate=d["yield_rate"],
            )
            for d in data
        ]

    def find_by_id(self, sample_id: str) -> Optional[Sample]:
        return next((s for s in self.find_all() if s.sample_id == sample_id), None)
