import unittest
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, timedelta

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.engine import BacktestEngine
from src.config import Config

class TestBacktestEngine(unittest.TestCase):

    def setUp(self):
        """Set up for the tests."""
        self.config = Config('src/config/default.yaml')
        self.config.set('cache_dir', 'test_cache')
        self.engine = BacktestEngine(self.config)
        
        close_prices = [100 + i * 0.5 - (i // 20) * 5 for i in range(100)]
        
        self.sample_data = pd.DataFrame({
            'open': close_prices,
            'high': [p + 1 for p in close_prices],
            'low': [p - 1 for p in close_prices],
            'close': close_prices,
            'volume': np.random.randint(1000, 5000, size=100),
            'symbol': 'TEST'
        }, index=pd.to_datetime(pd.date_range(start='2023-01-01', periods=100)))
        
        self.engine.data_manager.fetch_data = lambda symbols, start_date, end_date, timeframe="1d": {'TEST': self.sample_data}

    async def test_backtest_execution(self):
        """Test that the engine can run a simple backtest."""
        results = await self.engine.run_backtest(
            strategy_name='moving_average_crossover',
            symbols=['TEST'],
            start_date='2023-01-01',
            end_date='2023-04-10',
            fast_period=10,
            slow_period=30
        )
        
        self.assertIsNotNone(results)
        self.assertIn('performance', results)
        self.assertIn('total_return', results['performance'])

    async def test_order_creation_and_execution(self):
        """Test that orders are created and executed correctly."""
        results = await self.engine.run_backtest(
            strategy_name='moving_average_crossover',
            symbols=['TEST'],
            start_date='2023-01-01',
            end_date='2023-04-10',
            fast_period=10,
            slow_period=30
        )
        
        closed_positions = results.get('positions', [])
        self.assertGreater(len(closed_positions), 0)
        
        for pos in closed_positions:
            for order in pos.orders:
                self.assertEqual(order.status.value, 'filled')

    async def test_position_tracking(self):
        """Verify that positions are tracked properly."""
        results = await self.engine.run_backtest(
            strategy_name='moving_average_crossover',
            symbols=['TEST'],
            start_date='2023-01-01',
            end_date='2023-04-10',
            fast_period=10,
            slow_period=30
        )
        
        closed_positions = results.get('positions', [])
        self.assertGreater(len(closed_positions), 0)
        
        for pos in closed_positions:
            self.assertNotEqual(pos.get_pnl(), 0)

    async def test_performance_calculation(self):
        """Check that performance metrics are calculated correctly."""
        results = await self.engine.run_backtest(
            strategy_name='moving_average_crossover',
            symbols=['TEST'],
            start_date='2023-01-01',
            end_date='2023-04-10',
            fast_period=10,
            slow_period=30
        )
        
        performance = results.get('performance', {})
        self.assertNotEqual(performance.get('total_return', 0), 0)
        self.assertNotEqual(performance.get('sharpe_ratio', 0), 0)
        self.assertNotEqual(performance.get('max_drawdown', 0), 0)

if __name__ == '__main__':
    unittest.main()