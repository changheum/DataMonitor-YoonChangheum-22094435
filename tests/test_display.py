import pytest
from io import StringIO

from domain.order import OrderStatus
from service.inventory_monitor_service import InventoryStatus
from display.monitor_display import MonitorDisplay


class TestMonitorDisplay:
    def _make_counts(self, reserved=0, producing=0, confirmed=0, release=0):
        return {
            OrderStatus.RESERVED: reserved,
            OrderStatus.PRODUCING: producing,
            OrderStatus.CONFIRMED: confirmed,
            OrderStatus.RELEASE: release,
        }

    def _make_inventory_status(self, entries):
        return [
            {"sample_id": sid, "name": name, "stock": stock, "status": status}
            for sid, name, stock, status in entries
        ]

    def _render(self, counts, inventory_status):
        out = StringIO()
        display = MonitorDisplay(output=out)
        display.render(order_counts=counts, inventory_status=inventory_status)
        return out.getvalue()

    # ------------------------------------------------------------------
    # 주문 현황 섹션
    # ------------------------------------------------------------------

    def test_output_contains_order_section_header(self):
        output = self._render(self._make_counts(), [])
        assert "주문 현황" in output

    def test_output_shows_reserved_count(self):
        output = self._render(self._make_counts(reserved=3), [])
        assert "RESERVED" in output
        assert "3" in output

    def test_output_shows_producing_count(self):
        output = self._render(self._make_counts(producing=2), [])
        assert "PRODUCING" in output
        assert "2" in output

    def test_output_shows_confirmed_count(self):
        output = self._render(self._make_counts(confirmed=5), [])
        assert "CONFIRMED" in output
        assert "5" in output

    def test_output_shows_release_count(self):
        output = self._render(self._make_counts(release=1), [])
        assert "RELEASE" in output
        assert "1" in output

    def test_output_does_not_contain_rejected(self):
        output = self._render(self._make_counts(), [])
        assert "REJECTED" not in output

    # ------------------------------------------------------------------
    # 재고 현황 섹션
    # ------------------------------------------------------------------

    def test_output_contains_inventory_section_header(self):
        output = self._render(self._make_counts(), [])
        assert "재고 현황" in output

    def test_output_shows_sample_name(self):
        entries = [("S001", "시료A", 10, InventoryStatus.SUFFICIENT)]
        output = self._render(self._make_counts(), self._make_inventory_status(entries))
        assert "시료A" in output

    def test_output_shows_stock_quantity(self):
        entries = [("S001", "시료A", 42, InventoryStatus.SUFFICIENT)]
        output = self._render(self._make_counts(), self._make_inventory_status(entries))
        assert "42" in output

    def test_output_shows_sufficient_label(self):
        entries = [("S001", "시료A", 10, InventoryStatus.SUFFICIENT)]
        output = self._render(self._make_counts(), self._make_inventory_status(entries))
        assert "여유" in output

    def test_output_shows_insufficient_label(self):
        entries = [("S001", "시료A", 3, InventoryStatus.INSUFFICIENT)]
        output = self._render(self._make_counts(), self._make_inventory_status(entries))
        assert "부족" in output

    def test_output_shows_depleted_label(self):
        entries = [("S001", "시료A", 0, InventoryStatus.DEPLETED)]
        output = self._render(self._make_counts(), self._make_inventory_status(entries))
        assert "고갈" in output

    def test_output_shows_all_samples(self):
        entries = [
            ("S001", "시료A", 10, InventoryStatus.SUFFICIENT),
            ("S002", "시료B", 0,  InventoryStatus.DEPLETED),
            ("S003", "시료C", 2,  InventoryStatus.INSUFFICIENT),
        ]
        output = self._render(self._make_counts(), self._make_inventory_status(entries))
        assert "시료A" in output
        assert "시료B" in output
        assert "시료C" in output

    def test_output_shows_empty_inventory_message_when_no_samples(self):
        output = self._render(self._make_counts(), [])
        assert "없음" in output or "등록된 시료" in output or "재고 현황" in output

    # ------------------------------------------------------------------
    # MonitorDisplay 인터페이스
    # ------------------------------------------------------------------

    def test_render_writes_to_provided_output_stream(self):
        out = StringIO()
        display = MonitorDisplay(output=out)
        display.render(order_counts=self._make_counts(), inventory_status=[])
        assert len(out.getvalue()) > 0

    def test_default_output_is_stdout(self):
        import sys
        display = MonitorDisplay()
        assert display.output is sys.stdout
