
import unittest
import pandas as pd
import numpy as np
import os
import sys
import shutil
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.config import Config
from src.data_manager import DataManager
from src.strategy_manager import StrategyManager
from src.order_manager import OrderManager
from src.engine import BacktestEngine
from src.performance import PerformanceAnalyzer
from src.optimizer import BasicOptimizer
from src.plotting import Plotter

class TestComprehensiveFramework(unittest.TestCase):
    """Comprehensive test suite for the entire backtesting framework."""
    
    def setUp(self):
        """Set up for the tests."""
        self.test_cache_dir = 'test_cache'
        self.test_output_dir = 'test_output'
        os.makedirs(self.test_cache_dir, exist_ok=True)
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        self.config = Config()
        self.config.set('cache_dir', self.test_cache_dir)
        self.engine = BacktestEngine(self.config)
        
        np.random.seed(42)
        dates = pd.date_range(start='2022-01-01', end='2022-12-31')
        close_prices = 100 + np.random.randn(len(dates)).cumsum()
        self.sample_data = pd.DataFrame({
            'open': close_prices - 0.5,
            'high': close_prices + 1,
            'low': close_prices - 1,
            'close': close_prices,
            'volume': np.random.randint(1000000, 5000000, size=len(dates)),
            'symbol': 'SPY'
        }, index=dates)
        
        self.engine.data_manager.fetch_data = lambda symbols, start_date, end_date, timeframe="1d": {'SPY': self.sample_data}
        plt.ioff()
    
    def tearDown(self):
        """Clean up after tests."""
        plt.close('all')
        for directory in [self.test_cache_dir, self.test_output_dir]:
            if os.path.exists(directory):
                shutil.rmtree(directory)
    
    async def test_full_backtest_workflow(self):
        """Test the complete backtest workflow from start to finish."""
        results = await self.engine.run_backtest(
            strategy_name='moving_average_crossover',
            symbols=['SPY'],
            start_date='2022-01-01',
            end_date='2022-12-31',
            fast_period=10,
            slow_period=30
        )
        
        self.assertIn('performance', results)
        self.assertGreater(len(results['positions']), 0)
        self.assertGreater(len(results['equity_curve']), 0)
    
    async def test_all_strategies(self):
        """Test all built-in strategies."""
        for strategy in ['moving_average_crossover', 'rsi_mean_reversion', 'macd']:
            with self.subTest(strategy=strategy):
                results = await self.engine.run_backtest(
                    strategy_name=strategy,
                    symbols=['SPY'],
                    start_date='2022-01-01',
                    end_date='2022-12-31'
                )
                self.assertIn('performance', results)

if __name__ == '__main__':
    unittest.main()
