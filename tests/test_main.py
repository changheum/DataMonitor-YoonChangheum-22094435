import json
import pytest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from main import run


@pytest.fixture
def data_dir(tmp_path) -> Path:
    orders = [
        {"order_id": "O001", "sample_id": "S001", "customer": "고객A", "quantity": 10, "status": "RESERVED"},
        {"order_id": "O002", "sample_id": "S002", "customer": "고객B", "quantity": 3,  "status": "PRODUCING"},
        {"order_id": "O003", "sample_id": "S001", "customer": "고객C", "quantity": 5,  "status": "CONFIRMED"},
        {"order_id": "O004", "sample_id": "S003", "customer": "고객D", "quantity": 2,  "status": "RELEASE"},
        {"order_id": "O005", "sample_id": "S002", "customer": "고객E", "quantity": 1,  "status": "REJECTED"},
    ]
    samples = [
        {"sample_id": "S001", "name": "시료A", "avg_production_time": 2.0, "yield_rate": 0.9},
        {"sample_id": "S002", "name": "시료B", "avg_production_time": 3.5, "yield_rate": 0.8},
        {"sample_id": "S003", "name": "시료C", "avg_production_time": 1.5, "yield_rate": 1.0},
    ]
    inventory = [
        {"sample_id": "S001", "stock_quantity": 5},
        {"sample_id": "S002", "stock_quantity": 0},
        {"sample_id": "S003", "stock_quantity": 100},
    ]
    (tmp_path / "orders.json").write_text(json.dumps(orders), encoding="utf-8")
    (tmp_path / "samples.json").write_text(json.dumps(samples), encoding="utf-8")
    (tmp_path / "inventory.json").write_text(json.dumps(inventory), encoding="utf-8")
    return tmp_path


class TestRun:
    def test_run_produces_output(self, data_dir, capsys):
        run(data_dir=data_dir)
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_run_shows_order_section(self, data_dir, capsys):
        run(data_dir=data_dir)
        output = capsys.readouterr().out
        assert "주문 현황" in output

    def test_run_shows_inventory_section(self, data_dir, capsys):
        run(data_dir=data_dir)
        output = capsys.readouterr().out
        assert "재고 현황" in output

    def test_run_shows_correct_reserved_count(self, data_dir, capsys):
        run(data_dir=data_dir)
        output = capsys.readouterr().out
        assert "RESERVED" in output
        assert "1" in output

    def test_run_shows_sample_names(self, data_dir, capsys):
        run(data_dir=data_dir)
        output = capsys.readouterr().out
        assert "시료A" in output
        assert "시료B" in output
        assert "시료C" in output

    def test_run_shows_depleted_for_zero_stock(self, data_dir, capsys):
        run(data_dir=data_dir)
        output = capsys.readouterr().out
        assert "고갈" in output

    def test_run_works_with_missing_data_files(self, tmp_path, capsys):
        run(data_dir=tmp_path)
        output = capsys.readouterr().out
        assert "주문 현황" in output
        assert "재고 현황" in output
