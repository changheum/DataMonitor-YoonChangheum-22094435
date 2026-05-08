from pathlib import Path

from display.monitor_display import MonitorDisplay
from repository.inventory_repository import JsonInventoryRepository
from repository.order_repository import JsonOrderRepository
from repository.sample_repository import JsonSampleRepository
from service.inventory_monitor_service import InventoryMonitorService
from service.order_monitor_service import OrderMonitorService

DATA_DIR = Path(__file__).parent / "data"


def run(data_dir: Path = DATA_DIR) -> None:
    orders = JsonOrderRepository(data_dir / "orders.json").find_all()
    samples = JsonSampleRepository(data_dir / "samples.json").find_all()
    inventory = JsonInventoryRepository(data_dir / "inventory.json").find_all()

    order_counts = OrderMonitorService(orders=orders).get_order_counts()
    inventory_status = InventoryMonitorService(
        samples=samples, inventory=inventory, orders=orders
    ).get_inventory_status()

    MonitorDisplay().render(order_counts=order_counts, inventory_status=inventory_status)


if __name__ == "__main__":
    run()
