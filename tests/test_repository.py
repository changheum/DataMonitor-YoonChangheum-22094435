import json
import pytest
from pathlib import Path

from domain.order import Order, OrderStatus
from domain.sample import Sample
from domain.inventory import InventoryItem
from repository.order_repository import OrderRepository, JsonOrderRepository
from repository.sample_repository import SampleRepository, JsonSampleRepository
from repository.inventory_repository import InventoryRepository, JsonInventoryRepository


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def orders_json(tmp_path) -> Path:
    data = [
        {"order_id": "O001", "sample_id": "S001", "customer": "고객A", "quantity": 10, "status": "RESERVED"},
        {"order_id": "O002", "sample_id": "S002", "customer": "고객B", "quantity": 5,  "status": "PRODUCING"},
        {"order_id": "O003", "sample_id": "S001", "customer": "고객C", "quantity": 3,  "status": "CONFIRMED"},
        {"order_id": "O004", "sample_id": "S003", "customer": "고객D", "quantity": 7,  "status": "RELEASE"},
        {"order_id": "O005", "sample_id": "S002", "customer": "고객E", "quantity": 2,  "status": "REJECTED"},
    ]
    path = tmp_path / "orders.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture
def samples_json(tmp_path) -> Path:
    data = [
        {"sample_id": "S001", "name": "시료A", "avg_production_time": 2.0, "yield_rate": 0.9},
        {"sample_id": "S002", "name": "시료B", "avg_production_time": 3.5, "yield_rate": 0.8},
        {"sample_id": "S003", "name": "시료C", "avg_production_time": 1.5, "yield_rate": 1.0},
    ]
    path = tmp_path / "samples.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture
def inventory_json(tmp_path) -> Path:
    data = [
        {"sample_id": "S001", "stock_quantity": 50},
        {"sample_id": "S002", "stock_quantity": 0},
        {"sample_id": "S003", "stock_quantity": 20},
    ]
    path = tmp_path / "inventory.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# OrderRepository
# ---------------------------------------------------------------------------

class TestJsonOrderRepository:
    def test_find_all_returns_all_orders(self, orders_json):
        repo = JsonOrderRepository(orders_json)
        orders = repo.find_all()
        assert len(orders) == 5

    def test_find_all_returns_order_instances(self, orders_json):
        repo = JsonOrderRepository(orders_json)
        for order in repo.find_all():
            assert isinstance(order, Order)

    def test_find_all_maps_status_correctly(self, orders_json):
        repo = JsonOrderRepository(orders_json)
        orders = {o.order_id: o for o in repo.find_all()}
        assert orders["O001"].status == OrderStatus.RESERVED
        assert orders["O002"].status == OrderStatus.PRODUCING
        assert orders["O003"].status == OrderStatus.CONFIRMED
        assert orders["O004"].status == OrderStatus.RELEASE
        assert orders["O005"].status == OrderStatus.REJECTED

    def test_find_all_maps_fields_correctly(self, orders_json):
        repo = JsonOrderRepository(orders_json)
        order = repo.find_all()[0]
        assert order.order_id == "O001"
        assert order.sample_id == "S001"
        assert order.customer == "고객A"
        assert order.quantity == 10

    def test_find_all_returns_empty_list_when_file_not_found(self, tmp_path):
        repo = JsonOrderRepository(tmp_path / "nonexistent.json")
        assert repo.find_all() == []

    def test_json_order_repository_implements_interface(self, orders_json):
        repo = JsonOrderRepository(orders_json)
        assert isinstance(repo, OrderRepository)


# ---------------------------------------------------------------------------
# SampleRepository
# ---------------------------------------------------------------------------

class TestJsonSampleRepository:
    def test_find_all_returns_all_samples(self, samples_json):
        repo = JsonSampleRepository(samples_json)
        samples = repo.find_all()
        assert len(samples) == 3

    def test_find_all_returns_sample_instances(self, samples_json):
        repo = JsonSampleRepository(samples_json)
        for sample in repo.find_all():
            assert isinstance(sample, Sample)

    def test_find_all_maps_fields_correctly(self, samples_json):
        repo = JsonSampleRepository(samples_json)
        sample = repo.find_all()[0]
        assert sample.sample_id == "S001"
        assert sample.name == "시료A"
        assert sample.avg_production_time == 2.0
        assert sample.yield_rate == 0.9

    def test_find_all_returns_empty_list_when_file_not_found(self, tmp_path):
        repo = JsonSampleRepository(tmp_path / "nonexistent.json")
        assert repo.find_all() == []

    def test_find_by_id_returns_matching_sample(self, samples_json):
        repo = JsonSampleRepository(samples_json)
        sample = repo.find_by_id("S002")
        assert sample is not None
        assert sample.name == "시료B"

    def test_find_by_id_returns_none_when_not_found(self, samples_json):
        repo = JsonSampleRepository(samples_json)
        assert repo.find_by_id("UNKNOWN") is None

    def test_json_sample_repository_implements_interface(self, samples_json):
        repo = JsonSampleRepository(samples_json)
        assert isinstance(repo, SampleRepository)


# ---------------------------------------------------------------------------
# InventoryRepository
# ---------------------------------------------------------------------------

class TestJsonInventoryRepository:
    def test_find_all_returns_all_items(self, inventory_json):
        repo = JsonInventoryRepository(inventory_json)
        items = repo.find_all()
        assert len(items) == 3

    def test_find_all_returns_inventory_item_instances(self, inventory_json):
        repo = JsonInventoryRepository(inventory_json)
        for item in repo.find_all():
            assert isinstance(item, InventoryItem)

    def test_find_all_maps_fields_correctly(self, inventory_json):
        repo = JsonInventoryRepository(inventory_json)
        items = {i.sample_id: i for i in repo.find_all()}
        assert items["S001"].stock_quantity == 50
        assert items["S002"].stock_quantity == 0
        assert items["S003"].stock_quantity == 20

    def test_find_all_returns_empty_list_when_file_not_found(self, tmp_path):
        repo = JsonInventoryRepository(tmp_path / "nonexistent.json")
        assert repo.find_all() == []

    def test_find_by_sample_id_returns_matching_item(self, inventory_json):
        repo = JsonInventoryRepository(inventory_json)
        item = repo.find_by_sample_id("S002")
        assert item is not None
        assert item.stock_quantity == 0

    def test_find_by_sample_id_returns_none_when_not_found(self, inventory_json):
        repo = JsonInventoryRepository(inventory_json)
        assert repo.find_by_sample_id("UNKNOWN") is None

    def test_json_inventory_repository_implements_interface(self, inventory_json):
        repo = JsonInventoryRepository(inventory_json)
        assert isinstance(repo, InventoryRepository)
