from datetime import date
from decimal import Decimal
from pathlib import Path
import sys
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from omni_erp.warehouse import (  # noqa: E402
    InsufficientStockError,
    Product,
    Warehouse,
    WarehouseService,
)


class WarehouseServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = WarehouseService()
        self.service.add_product(Product("P-0001", "SKU-0001", "Sample Product"))
        self.service.add_warehouse(Warehouse("WH-HCM", "Ho Chi Minh Main"))
        self.service.add_warehouse(Warehouse("WH-HN", "Ha Noi Branch"))

    def test_receive_stock_creates_lot_and_inbound_movement(self) -> None:
        lot = self.service.receive_stock(
            lot_id="LOT-0001",
            warehouse_id="WH-HCM",
            internal_sku="SKU-0001",
            quantity="10",
            unit_cost="25000",
            document_no="GRN-0001",
            received_date=date(2026, 7, 5),
        )

        self.assertEqual("LOT-0001", lot.lot_id)
        self.assertEqual(Decimal("10"), self.service.stock_on_hand(warehouse_id="WH-HCM"))
        self.assertEqual("inbound", self.service.movements[0].movement_type)
        self.assertEqual("GRN-0001", self.service.movements[0].document_no)

    def test_stock_is_tracked_per_warehouse(self) -> None:
        self.service.receive_stock(
            lot_id="LOT-HCM",
            warehouse_id="WH-HCM",
            internal_sku="SKU-0001",
            quantity="10",
            unit_cost="25000",
            document_no="GRN-HCM",
            received_date=date(2026, 7, 5),
        )
        self.service.receive_stock(
            lot_id="LOT-HN",
            warehouse_id="WH-HN",
            internal_sku="SKU-0001",
            quantity="3",
            unit_cost="26000",
            document_no="GRN-HN",
            received_date=date(2026, 7, 6),
        )

        self.assertEqual(Decimal("10"), self.service.stock_on_hand(warehouse_id="WH-HCM"))
        self.assertEqual(Decimal("3"), self.service.stock_on_hand(warehouse_id="WH-HN"))
        self.assertEqual(Decimal("13"), self.service.stock_on_hand(internal_sku="SKU-0001"))

    def test_issue_stock_uses_fifo_lots(self) -> None:
        self.service.receive_stock(
            lot_id="LOT-OLD",
            warehouse_id="WH-HCM",
            internal_sku="SKU-0001",
            quantity="5",
            unit_cost="20000",
            document_no="GRN-OLD",
            received_date=date(2026, 7, 1),
        )
        self.service.receive_stock(
            lot_id="LOT-NEW",
            warehouse_id="WH-HCM",
            internal_sku="SKU-0001",
            quantity="10",
            unit_cost="22000",
            document_no="GRN-NEW",
            received_date=date(2026, 7, 3),
        )

        movements = self.service.issue_stock_fifo(
            warehouse_id="WH-HCM",
            internal_sku="SKU-0001",
            quantity="8",
            document_no="SO-0001",
            issued_date=date(2026, 7, 5),
        )

        self.assertEqual(["LOT-OLD", "LOT-NEW"], [movement.lot_id for movement in movements])
        self.assertEqual([Decimal("5"), Decimal("3")], [movement.quantity for movement in movements])
        self.assertEqual(Decimal("0"), self.service.lots[0].qty_available)
        self.assertEqual(Decimal("7"), self.service.lots[1].qty_available)

    def test_insufficient_stock_does_not_mutate_lots(self) -> None:
        self.service.receive_stock(
            lot_id="LOT-0001",
            warehouse_id="WH-HCM",
            internal_sku="SKU-0001",
            quantity="2",
            unit_cost="25000",
            document_no="GRN-0001",
            received_date=date(2026, 7, 5),
        )

        with self.assertRaises(InsufficientStockError):
            self.service.issue_stock_fifo(
                warehouse_id="WH-HCM",
                internal_sku="SKU-0001",
                quantity="3",
                document_no="SO-0002",
                issued_date=date(2026, 7, 6),
            )

        self.assertEqual(Decimal("2"), self.service.stock_on_hand(warehouse_id="WH-HCM"))
        self.assertEqual(1, len(self.service.movements))


if __name__ == "__main__":
    unittest.main()
