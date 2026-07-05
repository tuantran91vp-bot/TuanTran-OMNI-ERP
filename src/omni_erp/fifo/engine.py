"""FIFO stock automation and costing."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from omni_erp.importers import NormalizedOrderLine
from omni_erp.warehouse import StockMovement, WarehouseService

from .models import FifoIssueResult


class FifoEngine:
    """Coordinate normalized order lines with warehouse FIFO stock operations."""

    def __init__(self, warehouse_service: WarehouseService) -> None:
        self.warehouse_service = warehouse_service

    def issue_order_line(
        self,
        *,
        order_line: NormalizedOrderLine,
        warehouse_id: str,
        document_no: str | None = None,
    ) -> FifoIssueResult:
        issue_document = document_no or order_line.order_id
        movements = self.warehouse_service.issue_stock_fifo(
            warehouse_id=warehouse_id,
            internal_sku=order_line.internal_sku,
            quantity=order_line.inventory_quantity,
            document_no=issue_document,
            issued_date=order_line.order_date,
        )
        return FifoIssueResult(
            document_no=issue_document,
            platform=order_line.platform,
            order_id=order_line.order_id,
            internal_sku=order_line.internal_sku,
            inventory_quantity=order_line.inventory_quantity,
            movements=movements,
            cost_of_goods_sold=self.cost_of_goods_sold(movements),
        )

    def return_stock(
        self,
        *,
        issue_result: FifoIssueResult,
        return_quantity: Decimal | int | str,
        document_no: str,
        returned_date: date,
    ) -> list[StockMovement]:
        remaining_return_qty = Decimal(str(return_quantity))
        if remaining_return_qty <= 0:
            raise ValueError("return_quantity must be positive")
        if remaining_return_qty > issue_result.inventory_quantity:
            raise ValueError("return_quantity cannot exceed issued quantity")

        return_movements: list[StockMovement] = []
        for movement in reversed(issue_result.movements):
            if remaining_return_qty == 0:
                break
            return_qty = min(movement.quantity, remaining_return_qty)
            if movement.lot_id is None:
                raise ValueError("cannot return movement without lot_id")
            return_movements.append(
                self.warehouse_service.return_stock_to_lot(
                    lot_id=movement.lot_id,
                    quantity=return_qty,
                    document_no=document_no,
                    returned_date=returned_date,
                )
            )
            remaining_return_qty -= return_qty

        return return_movements

    def adjust_stock(
        self,
        *,
        warehouse_id: str,
        internal_sku: str,
        quantity_delta: Decimal | int | str,
        document_no: str,
        adjustment_date: date,
        unit_cost: Decimal | int | str = "0",
    ) -> list[StockMovement]:
        return self.warehouse_service.adjust_stock(
            warehouse_id=warehouse_id,
            internal_sku=internal_sku,
            quantity_delta=quantity_delta,
            document_no=document_no,
            adjustment_date=adjustment_date,
            unit_cost=unit_cost,
        )

    @staticmethod
    def cost_of_goods_sold(movements: list[StockMovement]) -> Decimal:
        return sum((movement.quantity * (movement.unit_cost or Decimal("0")) for movement in movements), Decimal("0"))
