"""Reconciliation result models."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ReconciliationResult:
    platform: str
    order_id: str
    internal_sku: str
    gross_revenue: Decimal
    voucher_discount: Decimal
    shipping_fee: Decimal
    platform_fee: Decimal
    payment_fee: Decimal
    cod_amount: Decimal
    amount_received: Decimal
    cost_of_goods_sold: Decimal
    profit: Decimal
