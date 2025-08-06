
import asyncio
import uuid
from typing import Dict, List, Optional

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from order_manager import OrderManager, Order, OrderType, OrderDirection, OrderStatus

class OrderService:
    """Service for managing orders."""

    def __init__(self, order_manager: Optional[OrderManager] = None):
        """Initialize the order service."""
        self.order_manager = order_manager or OrderManager()

    async def create_order(
        self,
        symbol: str,
        quantity: float,
        order_type: str,
        direction: str,
        price: Optional[float] = None
    ) -> Order:
        """Create a new order asynchronously."""
        loop = asyncio.get_event_loop()
        order = await loop.run_in_executor(
            None,
            self.order_manager.create_order,
            symbol,
            quantity,
            OrderType(order_type),
            OrderDirection(direction),
            price
        )
        return order

    async def get_order(self, order_id: str) -> Optional[Order]:
        """Get an order by its ID."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.order_manager.orders.get, order_id
        )

    async def list_orders(self) -> List[Order]:
        """List all orders."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: list(self.order_manager.orders.values())
        )

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        order = await self.get_order(order_id)
        if order and order.status == OrderStatus.PENDING:
            order.status = OrderStatus.CANCELLED
            return True
        return False
