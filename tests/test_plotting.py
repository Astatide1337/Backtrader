
from typing import Any, Dict, List, cast
import unittest
from unittest.mock import Mock
import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from plotting import Plotter

class TestPlotter(unittest.TestCase):

    def setUp(self):
        """Set up for the tests."""
        self.plotter = Plotter()
        self.test_output_dir = 'test_plots'
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        # Create sample data for plotting
        self.sample_equity_curve = pd.DataFrame({
            'timestamp': pd.to_datetime(pd.date_range(start='2023-01-01', periods=100)),
            'equity': np.linspace(10000, 12000, 100)
        })
        
        self.sample_positions = [
            Mock(entry_time=pd.to_datetime('2023-01-10'), exit_time=pd.to_datetime('2023-01-20'), quantity=10, pnl=100),
            Mock(entry_time=pd.to_datetime('2023-02-05'), exit_time=pd.to_datetime('2023-02-15'), quantity=-5, pnl=-50)
        ]
        
        self.sample_optimization_results = {
            'all_results': [
                {'params': {'fast_period': 10, 'slow_period': 30}, 'score': 1.8},
                {'params': {'fast_period': 20, 'slow_period': 50}, 'score': 1.5}
            ]
        }

    def tearDown(self):
        """Tear down after the tests."""
        # Clean up test plot files
        for f in os.listdir(self.test_output_dir):
            os.remove(os.path.join(self.test_output_dir, f))
        os.rmdir(self.test_output_dir)

    def test_plot_generation(self):
        """Test that all plots are generated correctly."""
        plt.ioff()  # Turn off interactive mode
        
        with self.subTest(plot='equity_curve'):
            equity_curve = cast(List[Dict[str, Any]], self.sample_equity_curve.to_dict('records'))
            fig = self.plotter.plot_equity_curve(equity_curve) # type: ignore
            self.assertIsNotNone(fig)
        
        with self.subTest(plot='drawdown'):
            drawdown_curve = cast(List[Dict[str, Any]], self.sample_equity_curve.to_dict('records'))
            fig = self.plotter.plot_drawdown(drawdown_curve) # type: ignore
            self.assertIsNotNone(fig)
            
            

    def test_plot_saving(self):
        """Test that plots can be saved to files."""
        plt.ioff()  # Turn off interactive mode
        
        save_path = os.path.join(self.test_output_dir, 'equity.png')
        self.plotter.plot_equity_curve(self.sample_equity_curve.to_dict('records'), save_path=save_path) # type: ignore
        self.assertTrue(os.path.exists(save_path))

    def test_plot_content(self):
        """Verify that the plots display the expected information."""
        plt.ioff()  # Turn off interactive mode
        
        # Test equity curve title
        fig = self.plotter.plot_equity_curve(self.sample_equity_curve.to_dict('records'), title="Test Equity Curve") # type: ignore
        self.assertEqual(fig.axes[0].get_title(), "Test Equity Curve") # type: ignore
        
        # Test drawdown y-label
        fig = self.plotter.plot_drawdown(self.sample_equity_curve.to_dict('records')) # type: ignore
        self.assertEqual(fig.axes[0].get_ylabel(), "Drawdown (%)") # type: ignore

if __name__ == '__main__':
    # Mock the show function to avoid displaying plots during tests
    plt.show = lambda: None
    unittest.main()
