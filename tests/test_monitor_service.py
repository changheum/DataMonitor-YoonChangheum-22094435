import pytest
from domain.order import Order, OrderStatus
from domain.sample import Sample
from domain.inventory import InventoryItem
from service.order_monitor_service import OrderMonitorService
from service.inventory_monitor_service import InventoryMonitorService, InventoryStatus


# ---------------------------------------------------------------------------
# OrderMonitorService
# ---------------------------------------------------------------------------

class TestOrderMonitorService:
    def _make_order(self, order_id, sample_id, quantity, status):
        return Order(order_id=order_id, sample_id=sample_id, customer="고객", quantity=quantity, status=status)

    def test_get_order_counts_returns_all_monitored_statuses(self):
        service = OrderMonitorService(orders=[])
        counts = service.get_order_counts()
        assert set(counts.keys()) == {
            OrderStatus.RESERVED,
            OrderStatus.PRODUCING,
            OrderStatus.CONFIRMED,
            OrderStatus.RELEASE,
        }

    def test_get_order_counts_excludes_rejected(self):
        orders = [self._make_order("O001", "S001", 1, OrderStatus.REJECTED)]
        service = OrderMonitorService(orders=orders)
        counts = service.get_order_counts()
        assert OrderStatus.REJECTED not in counts

    def test_get_order_counts_zero_when_no_orders(self):
        service = OrderMonitorService(orders=[])
        counts = service.get_order_counts()
        assert all(v == 0 for v in counts.values())

    def test_get_order_counts_single_reserved(self):
        orders = [self._make_order("O001", "S001", 5, OrderStatus.RESERVED)]
        service = OrderMonitorService(orders=orders)
        counts = service.get_order_counts()
        assert counts[OrderStatus.RESERVED] == 1
        assert counts[OrderStatus.PRODUCING] == 0
        assert counts[OrderStatus.CONFIRMED] == 0
        assert counts[OrderStatus.RELEASE] == 0

    def test_get_order_counts_multiple_orders_per_status(self):
        orders = [
            self._make_order("O001", "S001", 5,  OrderStatus.RESERVED),
            self._make_order("O002", "S001", 3,  OrderStatus.RESERVED),
            self._make_order("O003", "S002", 10, OrderStatus.PRODUCING),
            self._make_order("O004", "S002", 2,  OrderStatus.CONFIRMED),
            self._make_order("O005", "S003", 7,  OrderStatus.RELEASE),
            self._make_order("O006", "S003", 1,  OrderStatus.RELEASE),
            self._make_order("O007", "S003", 4,  OrderStatus.REJECTED),
        ]
        service = OrderMonitorService(orders=orders)
        counts = service.get_order_counts()
        assert counts[OrderStatus.RESERVED] == 2
        assert counts[OrderStatus.PRODUCING] == 1
        assert counts[OrderStatus.CONFIRMED] == 1
        assert counts[OrderStatus.RELEASE] == 2

    def test_get_order_counts_only_rejected_orders_gives_all_zeros(self):
        orders = [
            self._make_order("O001", "S001", 5, OrderStatus.REJECTED),
            self._make_order("O002", "S002", 3, OrderStatus.REJECTED),
        ]
        service = OrderMonitorService(orders=orders)
        counts = service.get_order_counts()
        assert all(v == 0 for v in counts.values())


# ---------------------------------------------------------------------------
# InventoryMonitorService
# ---------------------------------------------------------------------------

class TestInventoryStatus:
    def test_sufficient_label_is_여유(self):
        assert InventoryStatus.SUFFICIENT.value == "여유"

    def test_insufficient_label_is_부족(self):
        assert InventoryStatus.INSUFFICIENT.value == "부족"

    def test_depleted_label_is_고갈(self):
        assert InventoryStatus.DEPLETED.value == "고갈"


class TestInventoryMonitorService:
    def _make_sample(self, sample_id, name="시료"):
        return Sample(sample_id=sample_id, name=name, avg_production_time=1.0, yield_rate=0.9)

    def _make_inventory(self, sample_id, stock):
        return InventoryItem(sample_id=sample_id, stock_quantity=stock)

    def _make_order(self, order_id, sample_id, quantity, status):
        return Order(order_id=order_id, sample_id=sample_id, customer="고객", quantity=quantity, status=status)

    def test_get_inventory_status_returns_one_entry_per_sample(self):
        samples = [self._make_sample("S001"), self._make_sample("S002")]
        inventory = [self._make_inventory("S001", 10), self._make_inventory("S002", 5)]
        service = InventoryMonitorService(samples=samples, inventory=inventory, orders=[])
        result = service.get_inventory_status()
        assert len(result) == 2

    def test_status_is_depleted_when_stock_is_zero(self):
        samples = [self._make_sample("S001")]
        inventory = [self._make_inventory("S001", 0)]
        service = InventoryMonitorService(samples=samples, inventory=inventory, orders=[])
        result = service.get_inventory_status()
        assert result[0]["status"] == InventoryStatus.DEPLETED

    def test_status_is_sufficient_when_stock_exceeds_active_order_quantity(self):
        samples = [self._make_sample("S001")]
        inventory = [self._make_inventory("S001", 20)]
        orders = [self._make_order("O001", "S001", 10, OrderStatus.RESERVED)]
        service = InventoryMonitorService(samples=samples, inventory=inventory, orders=orders)
        result = service.get_inventory_status()
        assert result[0]["status"] == InventoryStatus.SUFFICIENT

    def test_status_is_sufficient_when_stock_equals_active_order_quantity(self):
        samples = [self._make_sample("S001")]
        inventory = [self._make_inventory("S001", 10)]
        orders = [self._make_order("O001", "S001", 10, OrderStatus.RESERVED)]
        service = InventoryMonitorService(samples=samples, inventory=inventory, orders=orders)
        result = service.get_inventory_status()
        assert result[0]["status"] == InventoryStatus.SUFFICIENT

    def test_status_is_insufficient_when_stock_less_than_active_order_quantity(self):
        samples = [self._make_sample("S001")]
        inventory = [self._make_inventory("S001", 5)]
        orders = [self._make_order("O001", "S001", 10, OrderStatus.RESERVED)]
        service = InventoryMonitorService(samples=samples, inventory=inventory, orders=orders)
        result = service.get_inventory_status()
        assert result[0]["status"] == InventoryStatus.INSUFFICIENT

    def test_rejected_orders_excluded_from_active_quantity_calculation(self):
        samples = [self._make_sample("S001")]
        inventory = [self._make_inventory("S001", 5)]
        orders = [
            self._make_order("O001", "S001", 10, OrderStatus.REJECTED),
        ]
        service = InventoryMonitorService(samples=samples, inventory=inventory, orders=orders)
        result = service.get_inventory_status()
        # stock(5) > active_quantity(0) → 여유
        assert result[0]["status"] == InventoryStatus.SUFFICIENT

    def test_active_quantity_sums_across_multiple_orders(self):
        samples = [self._make_sample("S001")]
        inventory = [self._make_inventory("S001", 10)]
        orders = [
            self._make_order("O001", "S001", 6, OrderStatus.RESERVED),
            self._make_order("O002", "S001", 5, OrderStatus.PRODUCING),
        ]
        service = InventoryMonitorService(samples=samples, inventory=inventory, orders=orders)
        result = service.get_inventory_status()
        # active_quantity = 11, stock = 10 → 부족
        assert result[0]["status"] == InventoryStatus.INSUFFICIENT

    def test_result_entry_contains_sample_name_and_stock(self):
        samples = [self._make_sample("S001", name="시료A")]
        inventory = [self._make_inventory("S001", 42)]
        service = InventoryMonitorService(samples=samples, inventory=inventory, orders=[])
        result = service.get_inventory_status()
        assert result[0]["sample_id"] == "S001"
        assert result[0]["name"] == "시료A"
        assert result[0]["stock"] == 42

    def test_sample_with_no_inventory_record_treated_as_depleted(self):
        samples = [self._make_sample("S001")]
        service = InventoryMonitorService(samples=samples, inventory=[], orders=[])
        result = service.get_inventory_status()
        assert result[0]["status"] == InventoryStatus.DEPLETED
        assert result[0]["stock"] == 0

    def test_release_orders_excluded_from_active_quantity(self):
        samples = [self._make_sample("S001")]
        inventory = [self._make_inventory("S001", 3)]
        orders = [
            self._make_order("O001", "S001", 10, OrderStatus.RELEASE),
        ]
        service = InventoryMonitorService(samples=samples, inventory=inventory, orders=orders)
        result = service.get_inventory_status()
        # RELEASE는 이미 출고 완료 → active에서 제외 → stock(3) > 0 → 여유
        assert result[0]["status"] == InventoryStatus.SUFFICIENT
