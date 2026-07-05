"""Reconciliation calculations."""

from __future__ import annotations

from decimal import Decimal

from omni_erp.importers import NormalizedOrderLine

from .models import ReconciliationResult


def reconcile_order_line(
    *,
    order_line: NormalizedOrderLine,
    cost_of_goods_sold: Decimal | int | str,
    platform_fee: Decimal | int | str = "0",
    payment_fee: Decimal | int | str = "0",
    cod_amount: Decimal | int | str | None = None,
    amount_received: Decimal | int | str | None = None,
) -> ReconciliationResult:
    """Calculate revenue, fees, cash received, and profit for one order line."""

    cogs = _decimal(cost_of_goods_sold)
    marketplace_fee = _decimal(platform_fee)
    pay_fee = _decimal(payment_fee)
    cod = _decimal(cod_amount) if cod_amount is not None else order_line.buyer_paid_amount
    received = (
        _decimal(amount_received)
        if amount_received is not None
        else order_line.buyer_paid_amount - marketplace_fee - pay_fee
    )

    return ReconciliationResult(
        platform=order_line.platform,
        order_id=order_line.order_id,
        internal_sku=order_line.internal_sku,
        gross_revenue=order_line.gross_amount,
        voucher_discount=order_line.discount_amount,
        shipping_fee=order_line.shipping_fee,
        platform_fee=marketplace_fee,
        payment_fee=pay_fee,
        cod_amount=cod,
        amount_received=received,
        cost_of_goods_sold=cogs,
        profit=received - cogs,
    )


def _decimal(value: Decimal | int | str) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))
