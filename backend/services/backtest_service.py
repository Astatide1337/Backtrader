
"""
Backtest service module.

Refactors the existing BacktestEngine into a service-based architecture.
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Union
from datetime import datetime

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.async_engine import AsyncBacktestEngine
from config import Config
from strategy_manager import StrategyManager
from ..database import save_backtest_result_db, get_backtest_result_db, list_backtests_db, delete_backtest_db


class BacktestService:
    """Service for managing backtests."""
    
    def __init__(self):
        """Initialize the backtest service."""
        self.config = Config()
        self.strategy_manager = StrategyManager()
        
    async def run_backtest(
        self,
        strategy_name: str,
        symbol: str,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        initial_capital: float = 10000,
        parameters: Optional[Dict] = None
    ) -> Dict:
        """Run a backtest asynchronously."""
        
        backtest_id = str(uuid.uuid4())
        
        config = Config()
        config.set('initial_capital', initial_capital)
        if parameters:
            config.update(parameters)
        
        engine = AsyncBacktestEngine(config=config)
        
        result = await engine.run_backtest(
            strategy_name,
            symbol,
            start_date,
            end_date,
            **(parameters or {})
        )
        
        result['backtest_id'] = backtest_id
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, save_backtest_result_db, backtest_id, result)
        
        return result
    
    async def get_backtest_results(self, backtest_id: str) -> Optional[Dict]:
        """Get backtest results by ID."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, get_backtest_result_db, backtest_id)
    
    async def list_backtests(self) -> List[Dict]:
        """List all backtests."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, list_backtests_db)
    
    async def list_strategies(self) -> List[Dict]:
        """List available strategies."""
        strategies = self.strategy_manager.list_strategies()
        return [
            {
                'name': name,
                'description': getattr(strategy_class, '__doc__', ''),
                'parameters': getattr(strategy_class, 'params', {})
            }
            for name, strategy_class in strategies.items()
        ]
    
    async def delete_backtest(self, backtest_id: str) -> bool:
        """Delete a backtest."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, delete_backtest_db, backtest_id)
