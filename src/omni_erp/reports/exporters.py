"""CSV and PDF report exporters."""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

from .models import Report


CSV_HEADERS = [
    "order_date",
    "platform",
    "order_id",
    "internal_sku",
    "gross_revenue",
    "amount_received",
    "cost_of_goods_sold",
    "profit",
]


def export_report_csv(report: Report, output_path: str | Path) -> Path:
    """Export a report as UTF-8 BOM CSV that opens cleanly in Excel."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([report.title])
        writer.writerow(["total_orders", report.total_orders])
        writer.writerow(["total_revenue", report.total_revenue])
        writer.writerow(["total_amount_received", report.total_amount_received])
        writer.writerow(["total_cost_of_goods_sold", report.total_cost_of_goods_sold])
        writer.writerow(["total_profit", report.total_profit])
        writer.writerow([])
        writer.writerow(CSV_HEADERS)
        for row in report.rows:
            writer.writerow(
                [
                    row.order_date.isoformat(),
                    row.platform,
                    row.order_id,
                    row.internal_sku,
                    row.gross_revenue,
                    row.amount_received,
                    row.cost_of_goods_sold,
                    row.profit,
                ]
            )
    return path


def export_report_pdf(report: Report, output_path: str | Path) -> Path:
    """Export a compact one-page PDF using only the Python standard library."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = _report_lines(report)
    content = _pdf_text_stream(lines)
    pdf_bytes = _build_pdf(content)
    path.write_bytes(pdf_bytes)
    return path


def _report_lines(report: Report) -> list[str]:
    lines = [
        report.title,
        f"Total orders: {report.total_orders}",
        f"Total revenue: {report.total_revenue}",
        f"Amount received: {report.total_amount_received}",
        f"COGS: {report.total_cost_of_goods_sold}",
        f"Profit: {report.total_profit}",
        "",
        "Date | Platform | Order | SKU | Revenue | Profit",
    ]
    for row in report.rows[:24]:
        lines.append(
            " | ".join(
                [
                    row.order_date.isoformat(),
                    row.platform,
                    row.order_id,
                    row.internal_sku,
                    str(row.gross_revenue),
                    str(row.profit),
                ]
            )
        )
    if len(report.rows) > 24:
        lines.append(f"... {len(report.rows) - 24} more rows")
    return lines


def _pdf_text_stream(lines: list[str]) -> bytes:
    stream = StringIO()
    stream.write("BT\n/F1 10 Tf\n50 780 Td\n")
    for index, line in enumerate(lines):
        if index > 0:
            stream.write("0 -16 Td\n")
        stream.write(f"({_escape_pdf_text(line)}) Tj\n")
    stream.write("ET\n")
    return stream.getvalue().encode("latin-1", errors="replace")


def _build_pdf(content_stream: bytes) -> bytes:
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content_stream)).encode("ascii") + b" >>\nstream\n" + content_stream + b"endstream",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{object_number} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(pdf)


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
