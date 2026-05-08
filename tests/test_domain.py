import pytest
from domain.order import Order, OrderStatus
from domain.sample import Sample
from domain.inventory import InventoryItem


class TestOrderStatus:
    def test_has_five_distinct_statuses(self):
        statuses = [
            OrderStatus.RESERVED,
            OrderStatus.REJECTED,
            OrderStatus.PRODUCING,
            OrderStatus.CONFIRMED,
            OrderStatus.RELEASE,
        ]
        assert len(set(statuses)) == 5

    def test_status_names_match_prd(self):
        assert OrderStatus["RESERVED"].name == "RESERVED"
        assert OrderStatus["REJECTED"].name == "REJECTED"
        assert OrderStatus["PRODUCING"].name == "PRODUCING"
        assert OrderStatus["CONFIRMED"].name == "CONFIRMED"
        assert OrderStatus["RELEASE"].name == "RELEASE"


class TestOrder:
    def test_create_order_with_valid_data(self):
        order = Order(
            order_id="O001",
            sample_id="S001",
            customer="고객A",
            quantity=10,
            status=OrderStatus.RESERVED,
        )
        assert order.order_id == "O001"
        assert order.sample_id == "S001"
        assert order.customer == "고객A"
        assert order.quantity == 10
        assert order.status == OrderStatus.RESERVED

    def test_order_quantity_zero_raises_value_error(self):
        with pytest.raises(ValueError):
            Order(order_id="O001", sample_id="S001", customer="고객A", quantity=0, status=OrderStatus.RESERVED)

    def test_order_quantity_negative_raises_value_error(self):
        with pytest.raises(ValueError):
            Order(order_id="O001", sample_id="S001", customer="고객A", quantity=-5, status=OrderStatus.RESERVED)

    def test_order_id_empty_raises_value_error(self):
        with pytest.raises(ValueError):
            Order(order_id="", sample_id="S001", customer="고객A", quantity=10, status=OrderStatus.RESERVED)

    def test_sample_id_empty_raises_value_error(self):
        with pytest.raises(ValueError):
            Order(order_id="O001", sample_id="", customer="고객A", quantity=10, status=OrderStatus.RESERVED)

    def test_customer_empty_raises_value_error(self):
        with pytest.raises(ValueError):
            Order(order_id="O001", sample_id="S001", customer="", quantity=10, status=OrderStatus.RESERVED)

    def test_all_statuses_assignable_to_order(self):
        for status in OrderStatus:
            order = Order(order_id="O001", sample_id="S001", customer="고객A", quantity=1, status=status)
            assert order.status == status


class TestSample:
    def test_create_sample_with_valid_data(self):
        sample = Sample(sample_id="S001", name="시료A", avg_production_time=2.5, yield_rate=0.9)
        assert sample.sample_id == "S001"
        assert sample.name == "시료A"
        assert sample.avg_production_time == 2.5
        assert sample.yield_rate == 0.9

    def test_yield_rate_above_one_raises_value_error(self):
        with pytest.raises(ValueError):
            Sample(sample_id="S001", name="시료A", avg_production_time=2.5, yield_rate=1.1)

    def test_yield_rate_zero_raises_value_error(self):
        with pytest.raises(ValueError):
            Sample(sample_id="S001", name="시료A", avg_production_time=2.5, yield_rate=0.0)

    def test_yield_rate_negative_raises_value_error(self):
        with pytest.raises(ValueError):
            Sample(sample_id="S001", name="시료A", avg_production_time=2.5, yield_rate=-0.1)

    def test_yield_rate_exactly_one_is_valid(self):
        sample = Sample(sample_id="S001", name="시료A", avg_production_time=2.5, yield_rate=1.0)
        assert sample.yield_rate == 1.0

    def test_avg_production_time_zero_raises_value_error(self):
        with pytest.raises(ValueError):
            Sample(sample_id="S001", name="시료A", avg_production_time=0, yield_rate=0.9)

    def test_avg_production_time_negative_raises_value_error(self):
        with pytest.raises(ValueError):
            Sample(sample_id="S001", name="시료A", avg_production_time=-1.0, yield_rate=0.9)

    def test_sample_id_empty_raises_value_error(self):
        with pytest.raises(ValueError):
            Sample(sample_id="", name="시료A", avg_production_time=2.5, yield_rate=0.9)

    def test_sample_name_empty_raises_value_error(self):
        with pytest.raises(ValueError):
            Sample(sample_id="S001", name="", avg_production_time=2.5, yield_rate=0.9)


class TestInventoryItem:
    def test_create_inventory_item_with_valid_data(self):
        item = InventoryItem(sample_id="S001", stock_quantity=100)
        assert item.sample_id == "S001"
        assert item.stock_quantity == 100

    def test_stock_quantity_zero_is_valid(self):
        item = InventoryItem(sample_id="S001", stock_quantity=0)
        assert item.stock_quantity == 0

    def test_stock_quantity_negative_raises_value_error(self):
        with pytest.raises(ValueError):
            InventoryItem(sample_id="S001", stock_quantity=-1)

    def test_sample_id_empty_raises_value_error(self):
        with pytest.raises(ValueError):
            InventoryItem(sample_id="", stock_quantity=100)

    def test_is_depleted_when_stock_is_zero(self):
        item = InventoryItem(sample_id="S001", stock_quantity=0)
        assert item.is_depleted() is True

    def test_is_not_depleted_when_stock_is_positive(self):
        item = InventoryItem(sample_id="S001", stock_quantity=1)
        assert item.is_depleted() is False
