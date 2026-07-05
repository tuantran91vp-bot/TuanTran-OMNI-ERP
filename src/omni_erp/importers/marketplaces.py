"""Marketplace CSV row normalization."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from .models import NormalizedOrderLine
from .sku_mapper import SkuMapper


DEFAULT_MARKETPLACE_COLUMNS: dict[str, dict[str, str]] = {
    "Shopee": {
        "order_id": "Order ID",
        "order_date": "Order Creation Date",
        "platform_sku": "SKU Reference No.",
        "quantity": "Quantity",
        "gross_amount": "Product Subtotal",
        "discount_amount": "Seller Voucher",
        "shipping_fee": "Shipping Fee",
        "buyer_paid_amount": "Order Total",
        "currency": "Currency",
        "raw_status": "Order Status",
    },
    "TikTok Shop": {
        "order_id": "Order ID",
        "order_date": "Created Time",
        "platform_sku": "Seller SKU",
        "quantity": "Quantity",
        "gross_amount": "Subtotal",
        "discount_amount": "Seller Discount",
        "shipping_fee": "Shipping Fee",
        "buyer_paid_amount": "Order Amount",
        "currency": "Currency",
        "raw_status": "Order Status",
    },
    "Lazada": {
        "order_id": "orderItemId",
        "order_date": "createTime",
        "platform_sku": "sellerSku",
        "quantity": "quantity",
        "gross_amount": "itemPrice",
        "discount_amount": "sellerDiscountTotal",
        "shipping_fee": "shippingFee",
        "buyer_paid_amount": "paidPrice",
        "currency": "currency",
        "raw_status": "status",
    },
}


def import_marketplace_rows(
    *,
    platform: str,
    rows: list[dict[str, str]],
    sku_mapper: SkuMapper,
    column_map: dict[str, str] | None = None,
) -> list[NormalizedOrderLine]:
    """Normalize marketplace rows into order lines for warehouse and reconciliation."""

    columns = column_map or DEFAULT_MARKETPLACE_COLUMNS[platform]
    normalized_rows: list[NormalizedOrderLine] = []

    for row in rows:
        platform_sku = _read(row, columns, "platform_sku")
        sold_quantity = _decimal(_read(row, columns, "quantity"), default="1")
        mapping = sku_mapper.resolve(platform, platform_sku)
        normalized_rows.append(
            NormalizedOrderLine(
                platform=platform,
                order_id=_read(row, columns, "order_id"),
                order_date=_date(_read(row, columns, "order_date")),
                platform_sku=platform_sku,
                internal_sku=mapping.internal_sku,
                quantity=sold_quantity,
                inventory_quantity=sold_quantity * mapping.conversion_qty,
                gross_amount=_decimal(_read(row, columns, "gross_amount", default="0")),
                discount_amount=_decimal(_read(row, columns, "discount_amount", default="0")),
                shipping_fee=_decimal(_read(row, columns, "shipping_fee", default="0")),
                buyer_paid_amount=_decimal(_read(row, columns, "buyer_paid_amount", default="0")),
                currency=_read(row, columns, "currency", default="VND"),
                raw_status=_read(row, columns, "raw_status", default=""),
            )
        )

    return normalized_rows


def _read(row: dict[str, str], columns: dict[str, str], field: str, default: str | None = None) -> str:
    column_name = columns[field]
    value = row.get(column_name, default)
    if value is None:
        raise KeyError(f"missing required column {column_name}")
    return value.strip()


def _decimal(value: str, *, default: str = "0") -> Decimal:
    cleaned_value = value.replace(",", "").strip()
    if cleaned_value == "":
        cleaned_value = default
    try:
        return Decimal(cleaned_value)
    except InvalidOperation as exc:
        raise ValueError(f"invalid decimal value: {value}") from exc


def _date(value: str) -> date:
    normalized_value = value.strip()
    for date_format in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%d/%m/%Y %H:%M:%S"):
        try:
            return datetime.strptime(normalized_value, date_format).date()
        except ValueError:
            continue
    raise ValueError(f"unsupported date value: {value}")
