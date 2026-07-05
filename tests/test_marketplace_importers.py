from datetime import date
from decimal import Decimal
from pathlib import Path
import sys
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from omni_erp.importers import (  # noqa: E402
    NormalizedOrderLine,
    SkuMapper,
    SkuMapping,
    UnmappedSkuError,
    import_marketplace_rows,
)


class MarketplaceImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mapper = SkuMapper(
            [
                SkuMapping("Shopee", "SHP-RED", "SKU-RED", Decimal("1")),
                SkuMapping("TikTok Shop", "TT-BUNDLE", "SKU-BUNDLE", Decimal("2")),
                SkuMapping("Lazada", "LZD-BLUE", "SKU-BLUE", Decimal("1")),
            ]
        )

    def test_import_shopee_row(self) -> None:
        rows = [
            {
                "Order ID": "SHP-1001",
                "Order Creation Date": "2026-07-05 10:30:00",
                "SKU Reference No.": "SHP-RED",
                "Quantity": "2",
                "Product Subtotal": "200000",
                "Seller Voucher": "10000",
                "Shipping Fee": "15000",
                "Order Total": "205000",
                "Currency": "VND",
                "Order Status": "Completed",
            }
        ]

        result = import_marketplace_rows(platform="Shopee", rows=rows, sku_mapper=self.mapper)

        self.assertEqual(
            NormalizedOrderLine(
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
            ),
            result[0],
        )

    def test_import_tiktok_shop_applies_conversion_quantity(self) -> None:
        rows = [
            {
                "Order ID": "TT-1001",
                "Created Time": "05/07/2026 11:00:00",
                "Seller SKU": "TT-BUNDLE",
                "Quantity": "3",
                "Subtotal": "300000",
                "Seller Discount": "0",
                "Shipping Fee": "0",
                "Order Amount": "300000",
                "Currency": "VND",
                "Order Status": "Delivered",
            }
        ]

        result = import_marketplace_rows(platform="TikTok Shop", rows=rows, sku_mapper=self.mapper)

        self.assertEqual("SKU-BUNDLE", result[0].internal_sku)
        self.assertEqual(Decimal("3"), result[0].quantity)
        self.assertEqual(Decimal("6"), result[0].inventory_quantity)

    def test_import_lazada_row(self) -> None:
        rows = [
            {
                "orderItemId": "LZD-1001",
                "createTime": "2026-07-05",
                "sellerSku": "LZD-BLUE",
                "quantity": "1",
                "itemPrice": "150000",
                "sellerDiscountTotal": "5000",
                "shippingFee": "12000",
                "paidPrice": "157000",
                "currency": "VND",
                "status": "delivered",
            }
        ]

        result = import_marketplace_rows(platform="Lazada", rows=rows, sku_mapper=self.mapper)

        self.assertEqual("LZD-1001", result[0].order_id)
        self.assertEqual("SKU-BLUE", result[0].internal_sku)
        self.assertEqual(Decimal("157000"), result[0].buyer_paid_amount)

    def test_unmapped_platform_sku_raises_error(self) -> None:
        rows = [
            {
                "Order ID": "SHP-1002",
                "Order Creation Date": "2026-07-05",
                "SKU Reference No.": "UNKNOWN",
                "Quantity": "1",
                "Product Subtotal": "100000",
                "Seller Voucher": "0",
                "Shipping Fee": "0",
                "Order Total": "100000",
                "Currency": "VND",
                "Order Status": "Completed",
            }
        ]

        with self.assertRaises(UnmappedSkuError):
            import_marketplace_rows(platform="Shopee", rows=rows, sku_mapper=self.mapper)


if __name__ == "__main__":
    unittest.main()
