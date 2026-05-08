from dataclasses import dataclass


@dataclass
class Sample:
    sample_id: str
    name: str
    avg_production_time: float
    yield_rate: float

    def __post_init__(self):
        if not self.sample_id:
            raise ValueError("sample_id cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")
        if self.avg_production_time <= 0:
            raise ValueError("avg_production_time must be positive")
        if not (0 < self.yield_rate <= 1.0):
            raise ValueError("yield_rate must be in range (0, 1]")
