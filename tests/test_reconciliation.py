from datetime import date
from decimal import Decimal
from pathlib import Path
import sys
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from omni_erp.importers import NormalizedOrderLine  # noqa: E402
from omni_erp.reconciliation import reconcile_order_line  # noqa: E402


class ReconciliationTests(unittest.TestCase):
    def test_reconcile_revenue_fees_cod_received_and_profit(self) -> None:
        order_line = NormalizedOrderLine(
            platform="Shopee",
            order_id="SHP-1001",
            order_date=date(2026, 7, 5),
            platform_sku="SHP-RED",
            internal_sku="SKU-RED",
            quantity=Decimal("2"),
            inventory_quantity=Decimal("2"),
            gross_amount=Decimal("200000"),
            discount_amount=Decimal("10000"),
            shipping_fee=Decimal("15000"),
            buyer_paid_amount=Decimal("205000"),
            currency="VND",
            raw_status="Completed",
        )

        result = reconcile_order_line(
            order_line=order_line,
            cost_of_goods_sold="90000",
            platform_fee="12000",
            payment_fee="3000",
        )

        self.assertEqual(Decimal("200000"), result.gross_revenue)
        self.assertEqual(Decimal("10000"), result.voucher_discount)
        self.assertEqual(Decimal("15000"), result.shipping_fee)
        self.assertEqual(Decimal("205000"), result.cod_amount)
        self.assertEqual(Decimal("190000"), result.amount_received)
        self.assertEqual(Decimal("100000"), result.profit)

    def test_reconcile_accepts_explicit_amount_received_from_statement(self) -> None:
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

        result = reconcile_order_line(
            order_line=order_line,
            cost_of_goods_sold="70000",
            platform_fee="10000",
            payment_fee="2000",
            amount_received="142000",
        )

        self.assertEqual(Decimal("142000"), result.amount_received)
        self.assertEqual(Decimal("72000"), result.profit)


if __name__ == "__main__":
    unittest.main()
