import asyncio
from typing import Dict, List, Optional, Union
from datetime import datetime
import alpaca_trade_api as tradeapi

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data_manager import DataManager
from config import Config

class MarketDataService:
    """Service for managing market data."""

    def __init__(self, data_manager: Optional[DataManager] = None, config: Optional[Config] = None):
        """Initialize the market data service."""
        self.data_manager = data_manager or DataManager()
        self.config = config or Config()
        self.api = tradeapi.REST(
            self.config.get('alpaca')['api_key'],
            self.config.get('alpaca')['secret_key'],
            base_url=self.config.get('alpaca')['base_url']
        )
        self.conn = tradeapi.Stream(
            self.config.get('alpaca')['api_key'],
            self.config.get('alpaca')['secret_key'],
            base_url=self.config.get('alpaca')['base_url']
        )

    async def get_market_data(
        self, 
        symbol: str, 
        start_date: Optional[Union[str, datetime]] = None, 
        end_date: Optional[Union[str, datetime]] = None, 
        timeframe: str = "1d"
    ) -> List[Dict]:
        """Get historical market data."""
        import pandas as pd
        loop = asyncio.get_event_loop()
        data_dict = await loop.run_in_executor(
            None,
            self.data_manager.fetch_data,
            symbol,
            start_date or datetime.now(),  # Provide a default value for start_date
            end_date or datetime.now(),  # Provide a default value for end_date
            timeframe
        )
                # Extract the DataFrame from the dictionary
        data_df = data_dict.get(symbol, pd.DataFrame())

        # Reset index to make the timestamp a column, as the frontend expects it
        if isinstance(data_df.index, pd.DatetimeIndex):
            data_df = data_df.reset_index()

        return data_df.to_dict('records')

    async def start_streaming(self, symbols: List[str], broadcast_callback):
        """Start streaming real-time market data."""
        self.conn.subscribe_trades(broadcast_callback, *symbols)