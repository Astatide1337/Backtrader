import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from order_manager import OrderManager, OrderType, OrderDirection, SlippageModel

class TestRealism(unittest.TestCase):

    def setUp(self):
        """Set up for the tests."""
        self.sample_data = pd.DataFrame({
            'open': np.arange(100, 110, 1),
            'high': np.arange(100, 110, 1) + 0.5,
            'low': np.arange(100, 110, 1) - 0.5,
            'close': np.arange(100, 110, 1),
            'volume': np.arange(1000, 1100, 10)
        }, index=pd.to_datetime(pd.date_range(start='2023-01-01 09:30', periods=10, freq='T')))

    async def test_fixed_slippage(self):
        """Test that fixed slippage is applied correctly."""
        order_manager = OrderManager(slippage_model=SlippageModel.FIXED, slippage=0.01)
        order = order_manager.create_order('TEST', 100, OrderType.MARKET, OrderDirection.BUY)
        await order_manager.execute_order(order, 105.0, self.sample_data.index[-1], self.sample_data)
        
        self.assertAlmostEqual(order.filled_price, 105.01)

    async def test_percentage_slippage(self):
        """Test that percentage slippage is applied correctly."""
        order_manager = OrderManager(slippage_model=SlippageModel.PERCENTAGE, slippage=0.001)
        order = order_manager.create_order('TEST', 100, OrderType.MARKET, OrderDirection.BUY)
        await order_manager.execute_order(order, 105.0, self.sample_data.index[-1], self.sample_data)
        
        self.assertAlmostEqual(order.filled_price, 105.105)

    async def test_volatility_adjusted_slippage(self):
        """Test that volatility-adjusted slippage is applied correctly."""
        order_manager = OrderManager(slippage_model=SlippageModel.VOLATILITY_ADJUSTED, slippage=0.1)
        order = order_manager.create_order('TEST', 100, OrderType.MARKET, OrderDirection.BUY)
        await order_manager.execute_order(order, 105.0, self.sample_data.index[-1], self.sample_data)
        
        volatility = self.sample_data['close'].pct_change().rolling(20).std().iloc[-1]
        expected_slippage = 105.0 * volatility * 0.1
        self.assertAlmostEqual(order.filled_price, 105.0 + expected_slippage)

    async def test_order_fill_timing(self):
        """Test that order fill timing is applied correctly."""
        order_manager = OrderManager(order_fill_delay_ms=100)
        order = order_manager.create_order('TEST', 100, OrderType.MARKET, OrderDirection.BUY)
        
        start_time = datetime.now()
        await order_manager.execute_order(order, 105.0, self.sample_data.index[-1], self.sample_data)
        end_time = datetime.now()
        
        self.assertIsNotNone(order.filled_time)
        self.assertGreaterEqual((end_time - start_time).total_seconds() * 1000, 100)

if __name__ == '__main__':
    # Need to run the async tests in an event loop
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    # Asynchronous tests need to be discovered and wrapped
    for test_name in loader.getTestCaseNames(TestRealism):
        test = TestRealism(test_name)
        if asyncio.iscoroutinefunction(test.run):
            suite.addTest(unittest.FunctionTestCase(lambda: asyncio.run(test.run())))
        else:
            suite.addTest(test)

    runner = unittest.TextTestRunner()
    runner.run(suite)