from datetime import date
from decimal import Decimal
from pathlib import Path
import sys
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from omni_erp.fifo import FifoEngine  # noqa: E402
from omni_erp.importers import NormalizedOrderLine  # noqa: E402
from omni_erp.warehouse import Product, Warehouse, WarehouseService  # noqa: E402


class FifoEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = WarehouseService()
        self.service.add_product(Product("P-0001", "SKU-0001", "Sample Product"))
        self.service.add_warehouse(Warehouse("WH-HCM", "Ho Chi Minh Main"))
        self.service.receive_stock(
            lot_id="LOT-OLD",
            warehouse_id="WH-HCM",
            internal_sku="SKU-0001",
            quantity="5",
            unit_cost="10000",
            document_no="GRN-OLD",
            received_date=date(2026, 7, 1),
        )
        self.service.receive_stock(
            lot_id="LOT-NEW",
            warehouse_id="WH-HCM",
            internal_sku="SKU-0001",
            quantity="5",
            unit_cost="12000",
            document_no="GRN-NEW",
            received_date=date(2026, 7, 2),
        )
        self.engine = FifoEngine(self.service)

    def test_issue_order_line_calculates_cogs_from_fifo_lots(self) -> None:
        order_line = NormalizedOrderLine(
            platform="Shopee",
            order_id="SHP-1001",
            order_date=date(2026, 7, 5),
            platform_sku="SHP-RED",
            internal_sku="SKU-0001",
            quantity=Decimal("1"),
            inventory_quantity=Decimal("7"),
            gross_amount=Decimal("140000"),
            discount_amount=Decimal("0"),
            shipping_fee=Decimal("0"),
            buyer_paid_amount=Decimal("140000"),
            currency="VND",
            raw_status="Completed",
        )

        result = self.engine.issue_order_line(order_line=order_line, warehouse_id="WH-HCM")

        self.assertEqual(Decimal("74000"), result.cost_of_goods_sold)
        self.assertEqual(["LOT-OLD", "LOT-NEW"], [movement.lot_id for movement in result.movements])
        self.assertEqual(Decimal("3"), self.service.stock_on_hand(warehouse_id="WH-HCM"))

    def test_return_stock_restores_lot_quantity(self) -> None:
        order_line = NormalizedOrderLine(
            platform="Shopee",
            order_id="SHP-1002",
            order_date=date(2026, 7, 5),
            platform_sku="SHP-RED",
            internal_sku="SKU-0001",
            quantity=Decimal("1"),
            inventory_quantity=Decimal("6"),
            gross_amount=Decimal("120000"),
            discount_amount=Decimal("0"),
            shipping_fee=Decimal("0"),
            buyer_paid_amount=Decimal("120000"),
            currency="VND",
            raw_status="Completed",
        )
        issue_result = self.engine.issue_order_line(order_line=order_line, warehouse_id="WH-HCM")

        return_movements = self.engine.return_stock(
            issue_result=issue_result,
            return_quantity="2",
            document_no="RET-1002",
            returned_date=date(2026, 7, 6),
        )

        self.assertEqual("return", return_movements[0].movement_type)
        self.assertEqual(Decimal("6"), self.service.stock_on_hand(warehouse_id="WH-HCM"))

    def test_adjust_stock_can_increase_inventory(self) -> None:
        movements = self.engine.adjust_stock(
            warehouse_id="WH-HCM",
            internal_sku="SKU-0001",
            quantity_delta="3",
            document_no="ADJ-0001",
            adjustment_date=date(2026, 7, 7),
            unit_cost="11000",
        )

        self.assertEqual("adjustment", movements[0].movement_type)
        self.assertEqual(Decimal("13"), self.service.stock_on_hand(warehouse_id="WH-HCM"))

    def test_adjust_stock_can_decrease_inventory_with_fifo(self) -> None:
        movements = self.engine.adjust_stock(
            warehouse_id="WH-HCM",
            internal_sku="SKU-0001",
            quantity_delta="-6",
            document_no="ADJ-0002",
            adjustment_date=date(2026, 7, 7),
        )

        self.assertEqual(["adjustment", "adjustment"], [movement.movement_type for movement in movements])
        self.assertEqual(Decimal("4"), self.service.stock_on_hand(warehouse_id="WH-HCM"))
        self.assertEqual(["LOT-OLD", "LOT-NEW"], [movement.lot_id for movement in movements])


if __name__ == "__main__":
    unittest.main()
