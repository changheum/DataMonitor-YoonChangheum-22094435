from dataclasses import dataclass


@dataclass
class InventoryItem:
    sample_id: str
    stock_quantity: int

    def __post_init__(self):
        if not self.sample_id:
            raise ValueError("sample_id cannot be empty")
        if self.stock_quantity < 0:
            raise ValueError("stock_quantity cannot be negative")

    def is_depleted(self) -> bool:
        return self.stock_quantity == 0
