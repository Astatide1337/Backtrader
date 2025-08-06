

import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import pickle
import logging

class DataManager:
    """
    Handle data fetching and basic caching for the backtesting framework.
    """
    
    def __init__(self, cache_dir: str = "./data/cache"):
        """
        Initialize the data manager.
        
        Args:
            cache_dir: Directory to store cached data
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def fetch_data(self, symbols: Union[str, List[str]], start_date: Union[str, datetime], 
                   end_date: Union[str, datetime], timeframe: str = "1d") -> Dict[str, pd.DataFrame]:
        """
        Fetch market data for one or more symbols.
        
        Args:
            symbols: A single symbol or a list of symbols
            start_date: Start date for data fetch
            end_date: End date for data fetch
            timeframe: Data timeframe (1d, 1h, etc.)
            
        Returns:
            A dictionary of DataFrames, keyed by symbol
        """
        if isinstance(symbols, str):
            symbols = [symbols]

        data_dict = {}
        for symbol in symbols:
            data_dict[symbol] = self._fetch_single_symbol_data(symbol, start_date, end_date, timeframe)
        
        return data_dict

    def _fetch_single_symbol_data(self, symbol: str, start_date: Union[str, datetime], 
                                 end_date: Union[str, datetime], timeframe: str) -> pd.DataFrame:
        """Fetch data for a single symbol, using cache if available."""
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        if hasattr(start_date, 'tzinfo') and start_date.tzinfo is not None:
            start_date = start_date.replace(tzinfo=None)
        if hasattr(end_date, 'tzinfo') and end_date.tzinfo is not None:
            end_date = end_date.replace(tzinfo=None)

        cached_data = self.get_cached_data(symbol, start_date, end_date, timeframe)
        if cached_data is not None:
            self.logger.info(f"Using cached data for {symbol}")
            return cached_data
        
        try:
            self.logger.info(f"Fetching data for {symbol} from Yahoo Finance")
            data = yf.download(symbol, start=start_date, end=end_date, interval=timeframe)
            
            if data is None:
                self.logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
            elif data.empty:
                self.logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
            
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            data.columns = [col.lower().replace(' ', '_') for col in data.columns]
            data['symbol'] = symbol
            
            self.save_data(symbol, data, timeframe)
            return data
        
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_cached_data(self, symbol: str, start_date: datetime, 
                        end_date: datetime, timeframe: str) -> Optional[pd.DataFrame]:
        """Retrieve cached data for a single symbol."""
        cache_file = self._get_cache_file_path(symbol, timeframe)
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)

            if hasattr(cached_data.index, 'tz') and cached_data.index.tz is not None:
                cached_data.index = cached_data.index.tz_localize(None)
            
            if cached_data.index[0] <= start_date and cached_data.index[-1] >= end_date:
                mask = (cached_data.index >= start_date) & (cached_data.index <= end_date)
                return cached_data.loc[mask]
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error loading cached data for {symbol}: {e}")
            return None
    
    def save_data(self, symbol: str, data: pd.DataFrame, timeframe: str) -> None:
        """Save data for a single symbol to cache."""
        cache_file = self._get_cache_file_path(symbol, timeframe)
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            self.logger.info(f"Data for {symbol} cached to {cache_file}")
        except Exception as e:
            self.logger.error(f"Error caching data for {symbol}: {e}")
    
    def _get_cache_file_path(self, symbol: str, timeframe: str) -> str:
        """Get the cache file path for a symbol and timeframe."""
        safe_symbol = symbol.replace('/', '_').replace('\\', '_')
        return os.path.join(self.cache_dir, f"{safe_symbol}_{timeframe}.pkl")
