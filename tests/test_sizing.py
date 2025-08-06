
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.async_engine import AsyncBacktestEngine
from config import Config

class TestSizing(unittest.TestCase):

    def setUp(self):
        """Set up for the tests."""
        self.config = Config()
        self.config.set('use_volatility_adjusted_sizing', True)
        self.config.set('volatility_window', 10)
        self.config.set('risk_per_trade', 0.01)
        self.engine = AsyncBacktestEngine(self.config)
        
        self.sample_data = pd.DataFrame({
            'open': np.arange(100, 120, 1),
            'high': np.arange(100, 120, 1) + 0.5,
            'low': np.arange(100, 120, 1) - 0.5,
            'close': np.arange(100, 120, 1),
            'volume': np.random.randint(1000, 5000, size=20),
            'symbol': 'TEST'
        }, index=pd.to_datetime(pd.date_range(start='2023-01-01', periods=20)))
        self.sample_data['signal'] = 0
        self.sample_data.loc[self.sample_data.index[10], 'signal'] = 1

    async def test_fixed_sizing(self):
        """Test that fixed sizing calculates the correct position size."""
        self.config.set('use_volatility_adjusted_sizing', False)
        self.engine = AsyncBacktestEngine(self.config)
        
        await self.engine._step_through_data(self.sample_data, unittest.mock.Mock())
        
        self.assertGreater(len(self.engine.order_manager.orders), 0)
        order = list(self.engine.order_manager.orders.values())[0]
        
        expected_quantity = self.engine.initial_capital / self.sample_data['close'].iloc[10]
        self.assertAlmostEqual(order.quantity, expected_quantity)

    async def test_volatility_adjusted_sizing(self):
        """Test that volatility-adjusted sizing calculates the correct position size."""
        await self.engine._step_through_data(self.sample_data, unittest.mock.Mock())
        
        self.assertGreater(len(self.engine.order_manager.orders), 0)
        order = list(self.engine.order_manager.orders.values())[0]
        
        volatility = self.sample_data['close'].pct_change().rolling(window=10).std().iloc[10] * np.sqrt(252)
        position_size = (self.engine.initial_capital * 0.01) / volatility
        expected_quantity = position_size / self.sample_data['close'].iloc[10]
        
        self.assertAlmostEqual(order.quantity, expected_quantity)

if __name__ == '__main__':
    # Need to run the async tests in an event loop
    import asyncio
    
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSizing))
    
    class AsyncTestRunner(unittest.TextTestRunner):
        def run(self, test):
            self.loop = asyncio.get_event_loop()
            return self.loop.run_until_complete(self.run_async(test))

        async def run_async(self, test):
            return await super().run(test)

    runner = AsyncTestRunner()
    runner.run(suite)
