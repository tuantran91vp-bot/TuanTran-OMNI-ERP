"""Google Sheet template schema validation."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


REQUIRED_SHEETS: dict[str, tuple[str, ...]] = {
    "products.csv": (
        "product_id",
        "product_name",
        "category",
        "brand",
        "unit",
        "status",
        "created_at",
        "notes",
    ),
    "sku_mapping.csv": (
        "platform",
        "platform_sku",
        "internal_sku",
        "product_id",
        "variant_name",
        "conversion_qty",
        "status",
    ),
    "warehouses.csv": (
        "warehouse_id",
        "warehouse_name",
        "warehouse_type",
        "address",
        "manager",
        "status",
    ),
    "suppliers.csv": (
        "supplier_id",
        "supplier_name",
        "contact_name",
        "phone",
        "email",
        "address",
        "status",
    ),
    "inventory_lots.csv": (
        "lot_id",
        "warehouse_id",
        "internal_sku",
        "supplier_id",
        "received_date",
        "qty_received",
        "qty_available",
        "unit_cost",
        "currency",
    ),
    "settings.csv": (
        "setting_key",
        "setting_value",
        "description",
    ),
}


@dataclass(frozen=True)
class TemplateValidationError:
    """A single template validation problem."""

    file_name: str
    message: str


def validate_template_directory(template_dir: str | Path) -> list[TemplateValidationError]:
    """Validate required Google Sheet CSV templates and their headers."""

    base_path = Path(template_dir)
    errors: list[TemplateValidationError] = []

    for file_name, expected_headers in REQUIRED_SHEETS.items():
        file_path = base_path / file_name
        if not file_path.exists():
            errors.append(TemplateValidationError(file_name, "missing required template"))
            continue

        with file_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.reader(csv_file)
            try:
                actual_headers = tuple(next(reader))
            except StopIteration:
                actual_headers = ()

        if actual_headers != expected_headers:
            errors.append(
                TemplateValidationError(
                    file_name,
                    f"invalid headers: expected {expected_headers}, got {actual_headers}",
                )
            )

    return errors
