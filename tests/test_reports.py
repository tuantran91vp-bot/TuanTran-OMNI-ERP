from datetime import date
from decimal import Decimal
from pathlib import Path
import sys
import tempfile
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from omni_erp.dashboard import DashboardOrderMetric  # noqa: E402
from omni_erp.reports import ReportFilters, build_report, export_report_csv, export_report_pdf  # noqa: E402


class ReportTests(unittest.TestCase):
    def test_build_report_filters_by_time_and_platform(self) -> None:
        report = build_report(
            title="Shopee July Report",
            order_metrics=_metrics(),
            filters=ReportFilters(
                start_date=date(2026, 7, 5),
                end_date=date(2026, 7, 5),
                platform="shopee",
            ),
        )

        self.assertEqual(1, report.total_orders)
        self.assertEqual("SHP-1001", report.rows[0].order_id)
        self.assertEqual(Decimal("200000"), report.total_revenue)
        self.assertEqual(Decimal("95000"), report.total_profit)

    def test_build_report_without_filters_sorts_rows_and_totals_all_platforms(self) -> None:
        report = build_report(title="All Platforms", order_metrics=list(reversed(_metrics())))

        self.assertEqual(["SHP-1001", "TT-1001", "LZD-1001"], [row.order_id for row in report.rows])
        self.assertEqual(3, report.total_orders)
        self.assertEqual(Decimal("650000"), report.total_revenue)
        self.assertEqual(Decimal("300000"), report.total_cost_of_goods_sold)
        self.assertEqual(Decimal("280000"), report.total_profit)

    def test_export_report_csv_creates_excel_compatible_file(self) -> None:
        report = build_report(title="All Platforms", order_metrics=_metrics())

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = export_report_csv(report, Path(tmp_dir) / "report.csv")
            content = output_path.read_text(encoding="utf-8-sig")

        self.assertIn("All Platforms", content)
        self.assertIn("order_date,platform,order_id,internal_sku", content)
        self.assertIn("2026-07-05,Shopee,SHP-1001,SKU-RED", content)

    def test_export_report_pdf_creates_valid_pdf_file(self) -> None:
        report = build_report(title="All Platforms", order_metrics=_metrics())

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = export_report_pdf(report, Path(tmp_dir) / "report.pdf")
            pdf_bytes = output_path.read_bytes()

        self.assertTrue(pdf_bytes.startswith(b"%PDF-1.4"))
        self.assertIn(b"All Platforms", pdf_bytes)
        self.assertIn(b"%%EOF", pdf_bytes)


def _metrics() -> list[DashboardOrderMetric]:
    return [
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
            platform="Lazada",
            order_id="LZD-1001",
            internal_sku="SKU-GREEN",
            gross_revenue=Decimal("150000"),
            amount_received=Decimal("135000"),
            cost_of_goods_sold=Decimal("60000"),
            profit=Decimal("55000"),
        ),
    ]


if __name__ == "__main__":
    unittest.main()
