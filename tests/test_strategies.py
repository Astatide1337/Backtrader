import unittest
import pandas as pd
import numpy as np
import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from src.strategy_manager import StrategyManager
from src.strategies import *  # Import all strategies
from src.strategies.base import Strategy


class TestStrategies(unittest.TestCase):

    def setUp(self):
        """Set up for the tests."""
        self.strategy_manager = StrategyManager()
        # Create a sample dataframe for testing
        self.sample_data = pd.DataFrame(
            {
                "open": np.random.rand(100) * 100,
                "high": np.random.rand(100) * 100 + 100,
                "low": np.random.rand(100) * 100,
                "close": np.random.rand(100) * 100,
                "volume": np.random.rand(100) * 10000,
            }
        )

    def test_strategy_instantiation(self):
        """Test that all strategies can be instantiated."""
        for name in self.strategy_manager.list_strategies():
            with self.subTest(strategy=name):
                strategy = self.strategy_manager.create_strategy(name)
                self.assertIsNotNone(strategy)
                self.assertIsInstance(strategy, Strategy)


    def test_indicator_calculation(self):
        """Test that strategies correctly calculate indicators."""
        for name in self.strategy_manager.list_strategies():
            with self.subTest(strategy=name):
                strategy = self.strategy_manager.create_strategy(name)
                self.assertIsNotNone(strategy)
                if strategy is not None:
                    data_with_indicators = strategy.calculate_indicators(
                        self.sample_data.copy()
                    )
                    self.assertIsInstance(data_with_indicators, pd.DataFrame)
                    # Check that some columns were added
                    self.assertGreater(
                        len(data_with_indicators.columns), len(self.sample_data.columns)
                    )
                else:
                    self.fail(f"Strategy {name} is None")

    def test_signal_generation(self):
        """Test that strategies correctly generate signals."""
        for name in self.strategy_manager.list_strategies():
            with self.subTest(strategy=name):
                strategy = self.strategy_manager.create_strategy(name)
                if strategy is not None:
                    data_with_indicators = strategy.calculate_indicators(
                        self.sample_data.copy()
                    )
                    signals = strategy.generate_signals(data_with_indicators)
                    self.assertIsInstance(signals, pd.Series)
                    self.assertEqual(len(signals), len(self.sample_data))
                    # Check that signals are valid (1, -1, or 0)
                    self.assertTrue(signals.isin([1, -1, 0]).all())
                else:
                    self.fail(f"Strategy {name} is None")

    def test_strategy_manager(self):
        """Verify that the StrategyManager can create and run strategies."""
        strategy_name = "moving_average_crossover"
        strategy = self.strategy_manager.create_strategy(
            strategy_name, fast_period=10, slow_period=30
        )
        
        if strategy is not None:
            result = self.strategy_manager.run_strategy(strategy, self.sample_data.copy())
            self.assertIsInstance(result, pd.DataFrame)
            self.assertIn("signal", result.columns)
            self.assertIn("sma_fast", result.columns)
            self.assertIn("sma_slow", result.columns)
        else:
            self.fail(f"Strategy {strategy_name} is None")


if __name__ == "__main__":
    unittest.main()
