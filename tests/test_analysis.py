
import unittest
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, timedelta

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.optimizer import BasicOptimizer
from src.performance import PerformanceAnalyzer
from src.config import Config

class TestAnalysis(unittest.TestCase):

    def setUp(self):
        """Set up for the tests."""
        self.config = Config('src/config/default.yaml')
        self.config.set('cache_dir', 'test_cache')
        self.optimizer = BasicOptimizer(config=self.config)
        
        # Create a sample backtest result
        self.sample_results = {
            'strategy': 'moving_average_crossover',
            'symbol': 'SPY',
            'start_date': '2023-01-01',
            'end_date': '2023-04-10',
            'initial_capital': 10000,
            'final_capital': 12000,
            'equity_curve': pd.DataFrame({
                'equity': np.linspace(10000, 12000, 100)
            }, index=pd.to_datetime(pd.date_range(start='2023-01-01', periods=100))),
            'positions': [],
            'performance': {
                'total_return': 0.20,
                'annualized_return': 0.80,
                'sharpe_ratio': 1.5,
                'max_drawdown': -0.10
            }
        }

    def test_performance_metrics(self):
        """Test that performance metrics are calculated correctly."""
        analyzer = PerformanceAnalyzer()
        
        # Convert equity curve to list of dicts format expected by calculate_metrics
        equity_curve = []
        for timestamp, equity in self.sample_results['equity_curve']['equity'].items():
            equity_curve.append({'timestamp': timestamp, 'equity': equity})
        
        metrics = analyzer.calculate_metrics(
            equity_curve=equity_curve, 
            positions=self.sample_results['positions'], 
            initial_capital=self.sample_results['initial_capital']
        )
        
        self.assertIsNotNone(metrics)
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('sortino_ratio', metrics)
        self.assertIn('calmar_ratio', metrics)

    def test_optimization_process(self):
        """Test that the optimization process works with a simple parameter grid."""
        param_grid = {
            'fast_period': [10, 20],
            'slow_period': [30, 50]
        }
        
        # Mock the backtest engine to return dummy results
        async def mock_run_backtest(strategy_name, symbols, start_date, end_date, **strategy_params):
            # Handle the case where symbols is a list of strings
            if isinstance(symbols, list):
                symbol = symbols[0]  # Use the first symbol in the list
            else:
                symbol = symbols
            
            return {
                'performance': {
                    'sharpe_ratio': np.random.rand()
                },
                'final_capital': np.random.randint(9000, 15000)
            }
        
        self.optimizer.engine.run_backtest = mock_run_backtest
        
        optimization_results = self.optimizer.grid_search(
            strategy_name='moving_average_crossover',
            symbol='SPY',
            start_date='2023-01-01',
            end_date='2023-04-10',
            param_grid=param_grid
        )
        
        self.assertIsNotNone(optimization_results)
        self.assertIn('best_params', optimization_results) # type: ignore
        self.assertIn('all_results', optimization_results) # type: ignore
        self.assertEqual(len(optimization_results['all_results']), 4) # type: ignore

    def test_report_generation(self):
        """Verify that reports are generated correctly."""
        # Mock optimization results
        optimization_results = {
            'best_params': {'fast_period': 10, 'slow_period': 30},
            'best_score': 1.8,
            'best_metrics': {'total_return': 0.25, 'sharpe_ratio': 1.8},
            'all_results': [
                {'params': {'fast_period': 10, 'slow_period': 30}, 'score': 1.8, 'final_capital': 12500},
                {'params': {'fast_period': 20, 'slow_period': 50}, 'score': 1.5, 'final_capital': 11500}
            ]
        }
        
        report = self.optimizer.generate_optimization_report(optimization_results)
        
        self.assertIsInstance(report, str)
        self.assertIn("BEST PARAMETERS", report)
        self.assertIn("BEST PERFORMANCE METRICS", report)
        self.assertIn("TOP 5 RESULTS", report)

if __name__ == '__main__':
    unittest.main()
