from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile
import unittest

from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from omni_erp.web_import import import_order_file  # noqa: E402


class WebImportTests(unittest.TestCase):
    def test_import_csv_orders(self) -> None:
        content = (
            "Order ID,Order Creation Date,SKU Reference No.,Product Subtotal,Gia von\n"
            "SHP-1001,2026-07-05,SKU-RED,200000,90000\n"
        ).encode("utf-8")

        orders = import_order_file(file_name="orders.csv", content=content, platform_hint="Shopee")

        self.assertEqual(
            [
                {
                    "date": "2026-07-05",
                    "platform": "Shopee",
                    "orderId": "SHP-1001",
                    "sku": "SKU-RED",
                    "revenue": 200000,
                    "cogs": 90000,
                }
            ],
            orders,
        )

    def test_import_xlsx_orders(self) -> None:
        content = _build_xlsx(
            [
                ["Order ID", "Order Creation Date", "Seller SKU", "Order Amount", "Gia von"],
                ["TT-1001", "05/07/2026", "SKU-BLUE", "300000", "150000"],
            ]
        )

        orders = import_order_file(file_name="orders.xlsx", content=content, platform_hint="TikTok Shop")

        self.assertEqual("TT-1001", orders[0]["orderId"])
        self.assertEqual("2026-07-05", orders[0]["date"])
        self.assertEqual("SKU-BLUE", orders[0]["sku"])
        self.assertEqual(300000, orders[0]["revenue"])
        self.assertEqual(150000, orders[0]["cogs"])


def _build_xlsx(rows: list[list[str]]) -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>""",
        )
        archive.writestr(
            "xl/workbook.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheets><sheet name="Orders" sheetId="1" r:id="rId1" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/></sheets>
</workbook>""",
        )
        archive.writestr("xl/worksheets/sheet1.xml", _sheet_xml(rows))
    return buffer.getvalue()


def _sheet_xml(rows: list[list[str]]) -> str:
    row_xml = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for col_index, value in enumerate(row):
            reference = f"{chr(ord('A') + col_index)}{row_index}"
            cells.append(f'<c r="{reference}" t="inlineStr"><is><t>{value}</t></is></c>')
        row_xml.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(row_xml)}</sheetData>'
        "</worksheet>"
    )


if __name__ == "__main__":
    unittest.main()
