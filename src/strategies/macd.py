import pandas as pd
from .base import Strategy

class MACDStrategy(Strategy):
    """
    MACD (Moving Average Convergence Divergence) strategy.
    
    Generates buy signals when the MACD line crosses above the signal line,
    and sell signals when the MACD line crosses below the signal line.
    """
    
    def __init__(self, fast_period=12, slow_period=26, signal_period=9, stop_loss_pct=3, take_profit_pct=8):
        """
        Initialize the strategy.
        
        Args:
            fast_period: Period for the fast EMA
            slow_period: Period for the slow EMA
            signal_period: Period for the signal line EMA
            stop_loss_pct: Stop loss percentage
            take_profit_pct: Take profit percentage
        """
        super().__init__(
            fast_period=fast_period,
            slow_period=slow_period,
            signal_period=signal_period,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct
        )
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the MACD indicators.
        
        Args:
            data: OHLCV data
            
        Returns:
            DataFrame with added indicator columns
        """
        data = data.copy()
        
        # Calculate EMAs
        ema_fast = data['close'].ewm(span=self.params['fast_period']).mean()
        ema_slow = data['close'].ewm(span=self.params['slow_period']).mean()
        
        # Calculate MACD line
        data['macd'] = ema_fast - ema_slow
        
        # Calculate signal line
        data['signal'] = data['macd'].ewm(span=self.params['signal_period']).mean()
        
        # Calculate histogram
        data['histogram'] = data['macd'] - data['signal']
        
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on MACD crossovers.
        
        Args:
            data: OHLCV data with indicators
            
        Returns:
            Series of signals (1=buy, -1=sell, 0=hold)
        """
        signals = pd.Series(0, index=data.index)
        
        # Bullish crossover (buy signal)
        signals[(data['macd'] > data['signal']) & 
                 (data['macd'].shift(1) <= data['signal'].shift(1))] = 1
        
        # Bearish crossover (sell signal)
        signals[(data['macd'] < data['signal']) & 
                 (data['macd'].shift(1) >= data['signal'].shift(1))] = -1
        
        return signals