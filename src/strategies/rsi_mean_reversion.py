import pandas as pd
import numpy as np
from .base import Strategy

class RSIMeanReversion(Strategy):
    """
    RSI Mean Reversion strategy.
    
    Generates buy signals when RSI falls below the oversold threshold,
    and sell signals when RSI rises above the overbought threshold.
    """
    
    def __init__(self, rsi_period=14, oversold=25, overbought=75, stop_loss_pct=4, take_profit_pct=10):
        """
        Initialize the strategy.
        
        Args:
            rsi_period: Period for RSI calculation
            oversold: Oversold threshold
            overbought: Overbought threshold
            stop_loss_pct: Stop loss percentage
            take_profit_pct: Take profit percentage
        """
        super().__init__(
            rsi_period=rsi_period,
            oversold=oversold,
            overbought=overbought,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct
        )
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the RSI indicator.
        
        Args:
            data: OHLCV data
            
        Returns:
            DataFrame with added indicator columns
        """
        data = data.copy()
        
        # Calculate RSI
        delta = data['close'].diff()
        delta = pd.to_numeric(delta, errors='coerce')
        gain = (delta.where(delta > 0, 0)).rolling(window=self.params['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.params['rsi_period']).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # Fill NaN values
        data.fillna(0, inplace=True)
        
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on RSI levels.
        
        Args:
            data: OHLCV data with indicators
            
        Returns:
            Series of signals (1=buy, -1=sell, 0=hold)
        """
        signals = pd.Series(0, index=data.index)
        
        # Oversold (buy signal)
        signals[data['rsi'] < self.params['oversold']] = 1
        
        # Overbought (sell signal)
        signals[data['rsi'] > self.params['overbought']] = -1
        
        return signals
