"""Import order files for the web app."""

from __future__ import annotations

import csv
from datetime import date, datetime, timedelta
from io import BytesIO, StringIO
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile


HEADER_ALIASES = {
    "date": ["order_date", "date", "ngay", "Order Creation Date", "Created Time", "createTime"],
    "platform": ["platform", "san", "marketplace"],
    "orderId": ["order_id", "orderId", "ma_don", "Order ID", "orderItemId"],
    "sku": ["sku", "internal_sku", "SKU Reference No.", "Seller SKU", "sellerSku"],
    "revenue": [
        "revenue",
        "gross_revenue",
        "doanh_thu",
        "Product Subtotal",
        "Subtotal",
        "itemPrice",
        "Order Total",
        "Order Amount",
        "paidPrice",
    ],
    "cogs": ["cogs", "cost_of_goods_sold", "gia_von", "Gia von"],
}


def import_order_file(*, file_name: str, content: bytes, platform_hint: str = "") -> list[dict[str, object]]:
    """Parse CSV/XLSX order files into web app order dictionaries."""

    suffix = Path(file_name).suffix.casefold()
    if suffix == ".csv":
        rows = _parse_csv(content)
    elif suffix == ".xlsx":
        rows = _parse_xlsx(content)
    else:
        raise ValueError("only .xlsx and .csv files are supported")
    return normalize_order_rows(rows, platform_hint=platform_hint)


def normalize_order_rows(rows: list[dict[str, str]], *, platform_hint: str = "") -> list[dict[str, object]]:
    """Normalize spreadsheet rows to the web app order shape."""

    normalized: list[dict[str, object]] = []
    for row in rows:
        order_id = _pick(row, "orderId")
        sku = _pick(row, "sku")
        if not order_id or not sku:
            continue

        normalized.append(
            {
                "date": _normalize_date(_pick(row, "date")),
                "platform": _pick(row, "platform") or platform_hint or "Unknown",
                "orderId": order_id,
                "sku": sku,
                "revenue": _number(_pick(row, "revenue")),
                "cogs": _number(_pick(row, "cogs")),
            }
        )
    return normalized


def _parse_csv(content: bytes) -> list[dict[str, str]]:
    text = content.decode("utf-8-sig")
    return [dict(row) for row in csv.DictReader(StringIO(text))]


def _parse_xlsx(content: bytes) -> list[dict[str, str]]:
    with ZipFile(BytesIO(content)) as workbook:
        shared_strings = _read_shared_strings(workbook)
        sheet_path = _first_sheet_path(workbook)
        sheet_xml = workbook.read(sheet_path)

    root = ElementTree.fromstring(sheet_xml)
    rows: list[list[str]] = []
    for row in root.findall(".//{*}sheetData/{*}row"):
        values: list[str] = []
        for cell in row.findall("{*}c"):
            index = _column_index(cell.attrib.get("r", ""))
            while len(values) <= index:
                values.append("")
            values[index] = _cell_value(cell, shared_strings)
        rows.append(values)

    if not rows:
        return []

    headers = [header.strip() for header in rows[0]]
    parsed_rows: list[dict[str, str]] = []
    for values in rows[1:]:
        parsed_rows.append(
            {
                header: values[index].strip() if index < len(values) else ""
                for index, header in enumerate(headers)
                if header
            }
        )
    return parsed_rows


def _read_shared_strings(workbook: ZipFile) -> list[str]:
    try:
        content = workbook.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    root = ElementTree.fromstring(content)
    strings: list[str] = []
    for item in root.findall("{*}si"):
        text_parts = [node.text or "" for node in item.findall(".//{*}t")]
        strings.append("".join(text_parts))
    return strings


def _first_sheet_path(workbook: ZipFile) -> str:
    if "xl/worksheets/sheet1.xml" in workbook.namelist():
        return "xl/worksheets/sheet1.xml"
    for name in workbook.namelist():
        if name.startswith("xl/worksheets/") and name.endswith(".xml"):
            return name
    raise ValueError("xlsx file does not contain a worksheet")


def _cell_value(cell: ElementTree.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.findall(".//{*}t"))

    value_node = cell.find("{*}v")
    if value_node is None or value_node.text is None:
        return ""

    if cell_type == "s":
        index = int(value_node.text)
        return shared_strings[index] if index < len(shared_strings) else ""
    return value_node.text


def _column_index(reference: str) -> int:
    letters = "".join(char for char in reference if char.isalpha()).upper()
    index = 0
    for char in letters:
        index = index * 26 + (ord(char) - ord("A") + 1)
    return max(index - 1, 0)


def _pick(row: dict[str, str], field: str) -> str:
    normalized_row = {key.strip().casefold(): value for key, value in row.items()}
    for alias in HEADER_ALIASES[field]:
        value = normalized_row.get(alias.casefold())
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _normalize_date(value: str) -> str:
    if not value:
        return date.today().isoformat()
    if value.replace(".", "", 1).isdigit():
        excel_epoch = datetime(1899, 12, 30)
        return (excel_epoch + timedelta(days=float(value))).date().isoformat()

    for date_format in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%d/%m/%Y %H:%M:%S"):
        try:
            return datetime.strptime(value, date_format).date().isoformat()
        except ValueError:
            continue
    return value[:10]


def _number(value: str) -> int:
    if not value:
        return 0
    cleaned = value.replace(",", "").replace("VND", "").replace("₫", "").strip()
    try:
        return int(float(cleaned))
    except ValueError:
        return 0
