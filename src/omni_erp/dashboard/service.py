"""Dashboard aggregation service."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal

from omni_erp.reconciliation import ReconciliationResult
from omni_erp.warehouse import InventoryLot

from .models import ChartPoint, DashboardOrderMetric, DashboardSummary, InventorySnapshot


def order_metric_from_reconciliation(
    *,
    order_date: date,
    reconciliation: ReconciliationResult,
) -> DashboardOrderMetric:
    """Create a dashboard metric from one reconciled order line."""

    return DashboardOrderMetric(
        order_date=order_date,
        platform=reconciliation.platform,
        order_id=reconciliation.order_id,
        internal_sku=reconciliation.internal_sku,
        gross_revenue=reconciliation.gross_revenue,
        amount_received=reconciliation.amount_received,
        cost_of_goods_sold=reconciliation.cost_of_goods_sold,
        profit=reconciliation.profit,
    )


def inventory_snapshots_from_lots(lots: list[InventoryLot]) -> list[InventorySnapshot]:
    """Aggregate available inventory quantity and value by warehouse and SKU."""

    grouped: dict[tuple[str, str], InventorySnapshot] = {}
    for lot in lots:
        key = (lot.warehouse_id, lot.internal_sku)
        current = grouped.get(
            key,
            InventorySnapshot(
                warehouse_id=lot.warehouse_id,
                internal_sku=lot.internal_sku,
                quantity_available=Decimal("0"),
                inventory_value=Decimal("0"),
            ),
        )
        grouped[key] = InventorySnapshot(
            warehouse_id=lot.warehouse_id,
            internal_sku=lot.internal_sku,
            quantity_available=current.quantity_available + lot.qty_available,
            inventory_value=current.inventory_value + (lot.qty_available * lot.unit_cost),
        )
    return sorted(grouped.values(), key=lambda item: (item.warehouse_id, item.internal_sku))


def build_dashboard_summary(
    *,
    order_metrics: list[DashboardOrderMetric],
    inventory_snapshots: list[InventorySnapshot],
) -> DashboardSummary:
    """Build KPI totals, chart points, and stock breakdowns for the dashboard."""

    revenue_by_platform: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    profit_by_platform: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    chart_rows: dict[date, dict[str, Decimal | int]] = {}

    total_revenue = Decimal("0")
    total_received = Decimal("0")
    total_cogs = Decimal("0")
    total_profit = Decimal("0")

    for metric in order_metrics:
        total_revenue += metric.gross_revenue
        total_received += metric.amount_received
        total_cogs += metric.cost_of_goods_sold
        total_profit += metric.profit
        revenue_by_platform[metric.platform] += metric.gross_revenue
        profit_by_platform[metric.platform] += metric.profit

        chart_row = chart_rows.setdefault(
            metric.order_date,
            {"revenue": Decimal("0"), "profit": Decimal("0"), "orders": 0},
        )
        chart_row["revenue"] = chart_row["revenue"] + metric.gross_revenue
        chart_row["profit"] = chart_row["profit"] + metric.profit
        chart_row["orders"] = chart_row["orders"] + 1

    stock_by_warehouse: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    stock_by_sku: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    total_stock_quantity = Decimal("0")
    total_inventory_value = Decimal("0")

    for snapshot in inventory_snapshots:
        total_stock_quantity += snapshot.quantity_available
        total_inventory_value += snapshot.inventory_value
        stock_by_warehouse[snapshot.warehouse_id] += snapshot.quantity_available
        stock_by_sku[snapshot.internal_sku] += snapshot.quantity_available

    chart_by_date = [
        ChartPoint(
            label=order_date.isoformat(),
            revenue=chart_row["revenue"],
            profit=chart_row["profit"],
            orders=int(chart_row["orders"]),
        )
        for order_date, chart_row in sorted(chart_rows.items())
    ]

    return DashboardSummary(
        total_orders=len(order_metrics),
        total_revenue=total_revenue,
        total_amount_received=total_received,
        total_cost_of_goods_sold=total_cogs,
        total_profit=total_profit,
        total_stock_quantity=total_stock_quantity,
        total_inventory_value=total_inventory_value,
        revenue_by_platform=dict(sorted(revenue_by_platform.items())),
        profit_by_platform=dict(sorted(profit_by_platform.items())),
        stock_by_warehouse=dict(sorted(stock_by_warehouse.items())),
        stock_by_sku=dict(sorted(stock_by_sku.items())),
        chart_by_date=chart_by_date,
    )
