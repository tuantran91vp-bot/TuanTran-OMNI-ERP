from datetime import date
from decimal import Decimal
from pathlib import Path
import sys
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from omni_erp.dashboard import (  # noqa: E402
    DashboardOrderMetric,
    build_dashboard_summary,
    inventory_snapshots_from_lots,
    order_metric_from_reconciliation,
)
from omni_erp.reconciliation import reconcile_order_line  # noqa: E402
from omni_erp.importers import NormalizedOrderLine  # noqa: E402
from omni_erp.warehouse import Product, Warehouse, WarehouseService  # noqa: E402


class DashboardTests(unittest.TestCase):
    def test_build_dashboard_summary_groups_kpis_charts_and_breakdowns(self) -> None:
        order_metrics = [
            DashboardOrderMetric(
                order_date=date(2026, 7, 5),
                platform="Shopee",
                order_id="SHP-1001",
                internal_sku="SKU-RED",
                gross_revenue=Decimal("200000"),
                amount_received=Decimal("185000"),
                cost_of_goods_sold=Decimal("90000"),
                profit=Decimal("95000"),
            ),
            DashboardOrderMetric(
                order_date=date(2026, 7, 5),
                platform="TikTok Shop",
                order_id="TT-1001",
                internal_sku="SKU-BLUE",
                gross_revenue=Decimal("300000"),
                amount_received=Decimal("280000"),
                cost_of_goods_sold=Decimal("150000"),
                profit=Decimal("130000"),
            ),
            DashboardOrderMetric(
                order_date=date(2026, 7, 6),
                platform="Shopee",
                order_id="SHP-1002",
                internal_sku="SKU-RED",
                gross_revenue=Decimal("100000"),
                amount_received=Decimal("93000"),
                cost_of_goods_sold=Decimal("40000"),
                profit=Decimal("53000"),
            ),
        ]
        inventory = [
            _inventory("WH-HCM", "SKU-RED", "8", "80000"),
            _inventory("WH-HCM", "SKU-BLUE", "2", "50000"),
            _inventory("WH-HN", "SKU-RED", "3", "33000"),
        ]

        summary = build_dashboard_summary(order_metrics=order_metrics, inventory_snapshots=inventory)

        self.assertEqual(3, summary.total_orders)
        self.assertEqual(Decimal("600000"), summary.total_revenue)
        self.assertEqual(Decimal("558000"), summary.total_amount_received)
        self.assertEqual(Decimal("280000"), summary.total_cost_of_goods_sold)
        self.assertEqual(Decimal("278000"), summary.total_profit)
        self.assertEqual({"Shopee": Decimal("300000"), "TikTok Shop": Decimal("300000")}, summary.revenue_by_platform)
        self.assertEqual({"Shopee": Decimal("148000"), "TikTok Shop": Decimal("130000")}, summary.profit_by_platform)
        self.assertEqual({"WH-HCM": Decimal("10"), "WH-HN": Decimal("3")}, summary.stock_by_warehouse)
        self.assertEqual({"SKU-BLUE": Decimal("2"), "SKU-RED": Decimal("11")}, summary.stock_by_sku)
        self.assertEqual(Decimal("13"), summary.total_stock_quantity)
        self.assertEqual(Decimal("163000"), summary.total_inventory_value)
        self.assertEqual(["2026-07-05", "2026-07-06"], [point.label for point in summary.chart_by_date])
        self.assertEqual([2, 1], [point.orders for point in summary.chart_by_date])

    def test_inventory_snapshots_from_lots_uses_available_quantity_and_fifo_cost(self) -> None:
        service = WarehouseService()
        service.add_product(Product("P-0001", "SKU-RED", "Red Product"))
        service.add_warehouse(Warehouse("WH-HCM", "Ho Chi Minh Main"))
        service.receive_stock(
            lot_id="LOT-OLD",
            warehouse_id="WH-HCM",
            internal_sku="SKU-RED",
            quantity="5",
            unit_cost="10000",
            document_no="GRN-OLD",
            received_date=date(2026, 7, 1),
        )
        service.receive_stock(
            lot_id="LOT-NEW",
            warehouse_id="WH-HCM",
            internal_sku="SKU-RED",
            quantity="5",
            unit_cost="12000",
            document_no="GRN-NEW",
            received_date=date(2026, 7, 2),
        )
        service.issue_stock_fifo(
            warehouse_id="WH-HCM",
            internal_sku="SKU-RED",
            quantity="6",
            document_no="SO-1001",
            issued_date=date(2026, 7, 5),
        )

        snapshots = inventory_snapshots_from_lots(service.lots)

        self.assertEqual(1, len(snapshots))
        self.assertEqual(Decimal("4"), snapshots[0].quantity_available)
        self.assertEqual(Decimal("48000"), snapshots[0].inventory_value)

    def test_order_metric_from_reconciliation_preserves_dashboard_fields(self) -> None:
        order_line = NormalizedOrderLine(
            platform="Lazada",
            order_id="LZD-1001",
            order_date=date(2026, 7, 5),
            platform_sku="LZD-BLUE",
            internal_sku="SKU-BLUE",
            quantity=Decimal("1"),
            inventory_quantity=Decimal("1"),
            gross_amount=Decimal("150000"),
            discount_amount=Decimal("5000"),
            shipping_fee=Decimal("12000"),
            buyer_paid_amount=Decimal("157000"),
            currency="VND",
            raw_status="delivered",
        )
        reconciliation = reconcile_order_line(
            order_line=order_line,
            cost_of_goods_sold="70000",
            platform_fee="10000",
            payment_fee="2000",
        )

        metric = order_metric_from_reconciliation(order_date=order_line.order_date, reconciliation=reconciliation)

        self.assertEqual("Lazada", metric.platform)
        self.assertEqual("LZD-1001", metric.order_id)
        self.assertEqual(Decimal("145000"), metric.amount_received)
        self.assertEqual(Decimal("75000"), metric.profit)


def _inventory(warehouse_id: str, internal_sku: str, quantity: str, value: str):
    from omni_erp.dashboard import InventorySnapshot

    return InventorySnapshot(
        warehouse_id=warehouse_id,
        internal_sku=internal_sku,
        quantity_available=Decimal(quantity),
        inventory_value=Decimal(value),
    )


if __name__ == "__main__":
    unittest.main()
