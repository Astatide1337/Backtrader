
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from unittest import IsolatedAsyncioTestCase

from src.order_manager import OrderManager, OrderType, OrderDirection

class TestExecution(IsolatedAsyncioTestCase):

    def setUp(self):
        """Set up for the tests."""
        self.order_manager = OrderManager()
        self.sample_data = pd.DataFrame({
            'open': np.arange(100, 110, 1),
            'high': np.arange(100, 110, 1) + 0.5,
            'low': np.arange(100, 110, 1) - 0.5,
            'close': np.arange(100, 110, 1),
            'volume': np.arange(1000, 1100, 10)
        }, index=pd.to_datetime(pd.date_range(start='2023-01-01 09:30', periods=10, freq='T')))

    async def test_vwap_execution(self):
        """Test that VWAP orders are executed at the correct price."""
        order = self.order_manager.create_order(
            symbol='TEST',
            quantity=100,
            order_type=OrderType.VWAP,
            direction=OrderDirection.BUY,
            duration=5
        )
        
        current_time = self.sample_data.index[-1]
        await self.order_manager.execute_order(order, self.sample_data['close'].iloc[-1], current_time, self.sample_data)
        
        self.assertIsNotNone(order.filled_price)
        
        # Calculate expected VWAP
        vwap_data = self.sample_data.iloc[-5:]
        expected_vwap = (vwap_data['close'] * vwap_data['volume']).sum() / vwap_data['volume'].sum()
        
        self.assertAlmostEqual(order.filled_price, expected_vwap)

    async def test_twap_execution(self):
        """Test that TWAP orders are executed at the correct price."""
        order = self.order_manager.create_order(
            symbol='TEST',
            quantity=100,
            order_type=OrderType.TWAP,
            direction=OrderDirection.BUY,
            duration=5
        )
        
        current_time = self.sample_data.index[-1]
        await self.order_manager.execute_order(order, self.sample_data['close'].iloc[-1], current_time, self.sample_data)
        
        self.assertIsNotNone(order.filled_price)
        
        # Calculate expected TWAP
        twap_data = self.sample_data.iloc[-5:]
        expected_twap = twap_data['close'].mean()
        
        self.assertIsInstance(order.filled_price, (int, float))
        self.assertAlmostEqual(order.filled_price, expected_twap) # type: ignore

if __name__ == '__main__':
    unittest.main()
