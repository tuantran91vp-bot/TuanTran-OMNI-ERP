"""Report building and filtering."""

from __future__ import annotations

from decimal import Decimal

from omni_erp.dashboard import DashboardOrderMetric

from .models import Report, ReportFilters, ReportRow


def build_report(
    *,
    title: str,
    order_metrics: list[DashboardOrderMetric],
    filters: ReportFilters | None = None,
) -> Report:
    """Build a date/platform-filtered report from dashboard order metrics."""

    active_filters = filters or ReportFilters()
    rows = [
        ReportRow(
            order_date=metric.order_date,
            platform=metric.platform,
            order_id=metric.order_id,
            internal_sku=metric.internal_sku,
            gross_revenue=metric.gross_revenue,
            amount_received=metric.amount_received,
            cost_of_goods_sold=metric.cost_of_goods_sold,
            profit=metric.profit,
        )
        for metric in order_metrics
        if _matches_filters(metric, active_filters)
    ]
    rows = sorted(rows, key=lambda row: (row.order_date, row.platform, row.order_id, row.internal_sku))

    return Report(
        title=title,
        filters=active_filters,
        rows=rows,
        total_orders=len(rows),
        total_revenue=sum((row.gross_revenue for row in rows), Decimal("0")),
        total_amount_received=sum((row.amount_received for row in rows), Decimal("0")),
        total_cost_of_goods_sold=sum((row.cost_of_goods_sold for row in rows), Decimal("0")),
        total_profit=sum((row.profit for row in rows), Decimal("0")),
    )


def _matches_filters(metric: DashboardOrderMetric, filters: ReportFilters) -> bool:
    if filters.start_date is not None and metric.order_date < filters.start_date:
        return False
    if filters.end_date is not None and metric.order_date > filters.end_date:
        return False
    if filters.platform is not None and metric.platform.casefold() != filters.platform.casefold():
        return False
    return True
