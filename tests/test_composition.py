
import unittest
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from strategies.base import Strategy
from strategies.components.moving_average import MovingAverageComponent
from strategies.components.rsi import RSIComponent

class TestComposition(unittest.TestCase):

    def setUp(self):
        """Set up for the tests."""
        self.sample_data = pd.DataFrame({
            'open': np.arange(100, 120, 1),
            'high': np.arange(100, 120, 1) + 0.5,
            'low': np.arange(100, 120, 1) - 0.5,
            'close': np.arange(100, 120, 1),
            'volume': np.random.randint(1000, 5000, size=20)
        }, index=pd.to_datetime(pd.date_range(start='2023-01-01', periods=20)))

    def test_composite_strategy(self):
        """Test that a composite strategy calculates indicators and generates signals correctly."""
        class CompositeStrategy(Strategy):
            def generate_signals(self, data: pd.DataFrame) -> pd.Series:
                signals = pd.Series(0, index=data.index)
                signals[data['sma_10'] > data['close']] = 1
                signals[data['rsi'] > 70] = -1
                return signals

        strategy = CompositeStrategy(components=[
            MovingAverageComponent(period=10),
            RSIComponent(period=14)
        ])

        data_with_indicators = strategy.calculate_indicators(self.sample_data.copy())
        self.assertIn('sma_10', data_with_indicators.columns)
        self.assertIn('rsi', data_with_indicators.columns)

        signals = strategy.generate_signals(data_with_indicators)
        self.assertEqual(len(signals), len(self.sample_data))
        self.assertTrue(signals.isin([1, -1, 0]).all())

if __name__ == '__main__':
    unittest.main()
