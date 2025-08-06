

import unittest
import os
import shutil
from datetime import datetime, timedelta
import sys

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.config import Config
from src.data_manager import DataManager

class TestSystem(unittest.TestCase):

    def setUp(self):
        """Set up for the tests."""
        self.config_path = 'src/config/default.yaml'
        self.cache_dir = 'test_cache'
        # Clean up cache directory before each test
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
        os.makedirs(self.cache_dir)

    def tearDown(self):
        """Tear down after the tests."""
        # Clean up cache directory
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)

    def test_config_loading(self):
        """Test that the configuration is loaded correctly."""
        config = Config(self.config_path)
        self.assertEqual(config.get('initial_capital'), 10000)
        self.assertEqual(config.get('data_source'), 'yahoo_finance')
        self.assertIsNotNone(config.get('strategy_params'))

    def test_data_fetching_and_caching(self):
        """Test fetching data and verifying caching."""
        config = Config(self.config_path)
        config.set('cache_dir', self.cache_dir)
        
        data_manager = DataManager(cache_dir=config.get('cache_dir'))
        
        symbol = 'AAPL'
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Fetch data for the first time
        print("\nFetching data for the first time...")
        data1 = data_manager.fetch_data(symbol, start_date, end_date)
        # fetch_data returns a dict of DataFrames keyed by symbol
        df1 = data1.get(symbol)
        self.assertIsNotNone(df1)
        self.assertFalse(df1.empty)
        self.assertIn('symbol', df1.columns)
        self.assertEqual(df1['symbol'].iloc[0], symbol)
        
        # Verify that the data is cached
        cache_file = data_manager._get_cache_file_path(symbol, '1d')
        self.assertTrue(os.path.exists(cache_file))
        
        # Fetch data for the second time
        print("\nFetching data for the second time (should be cached)...")
        data2 = data_manager.fetch_data(symbol, start_date, end_date)
        df2 = data2.get(symbol)
        self.assertIsNotNone(df2)
        self.assertFalse(df2.empty)
        
        # Verify that the data is the same for the symbol
        self.assertEqual(len(df1), len(df2))

if __name__ == '__main__':
    unittest.main()

