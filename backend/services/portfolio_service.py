
import asyncio
from typing import Dict, List, Optional

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from order_manager import OrderManager, Position
from performance import PerformanceAnalyzer

class PortfolioService:
    """Service for managing the portfolio."""

    def __init__(self, order_manager: Optional[OrderManager] = None):
        """Initialize the portfolio service."""
        self.order_manager = order_manager or OrderManager()

    async def get_portfolio_snapshot(self) -> Dict:
        """Get a snapshot of the current portfolio."""
        open_positions = await self.get_open_positions()
        closed_positions = await self.get_closed_positions()
        
        return {
            'open_positions': [p.__dict__ for p in open_positions],
            'closed_positions': [p.__dict__ for p in closed_positions],
            'performance': await self.calculate_performance()
        }

    async def get_open_positions(self) -> List[Position]:
        """Get all open positions."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.order_manager.get_open_positions
        )

    async def get_closed_positions(self) -> List[Position]:
        """Get all closed positions."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.order_manager.get_closed_positions
        )

    async def calculate_performance(self) -> Dict:
        """Calculate performance metrics for the portfolio."""
        # This is a placeholder. In a real implementation, we would need to
        # have the full equity curve and initial capital to calculate performance.
        # For now, we will just return some basic metrics.
        closed_positions = await self.get_closed_positions()
        if not closed_positions:
            return {}

        pnl = [p.get_pnl() for p in closed_positions]
        win_rate = len([p for p in pnl if p > 0]) / len(pnl)
        total_pnl = sum(pnl)

        return {
            'total_pnl': total_pnl,
            'win_rate': win_rate
        }
