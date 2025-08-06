
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.async_engine import AsyncBacktestEngine
from config import Config

class TestMultiAsset(unittest.TestCase):

    def setUp(self):
        """Set up for the tests."""
        self.config = Config()
        self.engine = AsyncBacktestEngine(self.config)
        
        self.sample_data_aapl = pd.DataFrame({
            'open': np.arange(100, 120, 1),
            'high': np.arange(100, 120, 1) + 0.5,
            'low': np.arange(100, 120, 1) - 0.5,
            'close': np.arange(100, 120, 1),
            'volume': np.random.randint(1000, 5000, size=20),
            'symbol': 'AAPL'
        }, index=pd.to_datetime(pd.date_range(start='2023-01-01', periods=20)))
        
        self.sample_data_goog = pd.DataFrame({
            'open': np.arange(200, 220, 1),
            'high': np.arange(200, 220, 1) + 0.5,
            'low': np.arange(200, 220, 1) - 0.5,
            'close': np.arange(200, 220, 1),
            'volume': np.random.randint(1000, 5000, size=20),
            'symbol': 'GOOG'
        }, index=pd.to_datetime(pd.date_range(start='2023-01-01', periods=20)))

        self.engine.data_manager.fetch_data = lambda symbols, start_date, end_date: {
            'AAPL': self.sample_data_aapl,
            'GOOG': self.sample_data_goog
        }

    async def test_multi_asset_backtest(self):
        """Test that the engine can run a backtest on multiple assets."""
        results = await self.engine.run_backtest(
            strategy_name='moving_average_crossover',
            symbols=['AAPL', 'GOOG'],
            start_date='2023-01-01',
            end_date='2023-01-20',
            fast_period=5,
            slow_period=10
        )
        
        self.assertIsNotNone(results)
        self.assertIn('positions', results)
        
        symbols_in_positions = {p.symbol for p in results['positions']}
        self.assertIn('AAPL', symbols_in_positions)
        self.assertIn('GOOG', symbols_in_positions)

if __name__ == '__main__':
    import asyncio
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMultiAsset))
    
    class AsyncTestRunner(unittest.TextTestRunner):
        def run(self, test):
            self.loop = asyncio.get_event_loop()
            return self.loop.run_until_complete(super().run(test))

    runner = AsyncTestRunner()
    runner.run(suite)
