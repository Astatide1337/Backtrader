import pandas as pd
from src.strategies.base import Strategy

class MovingAverageCrossover(Strategy):
    """
    Moving Average Crossover strategy.
    
    Generates buy signals when the fast moving average crosses above the slow moving average,
    and sell signals when the fast moving average crosses below the slow moving average.
    """
    
    def __init__(self, fast_period=50, slow_period=200, stop_loss_pct=3, take_profit_pct=8):
        """
        Initialize the strategy.
        
        Args:
            fast_period: Period for the fast moving average
            slow_period: Period for the slow moving average
            stop_loss_pct: Stop loss percentage
            take_profit_pct: Take profit percentage
        """
        super().__init__(
            fast_period=fast_period,
            slow_period=slow_period,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct
        )
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the moving averages.
        
        Args:
            data: OHLCV data
            
        Returns:
            DataFrame with added indicator columns
        """
        data = data.copy()
        
        # Calculate moving averages
        data['sma_fast'] = data['close'].rolling(self.params['fast_period']).mean()
        data['sma_slow'] = data['close'].rolling(self.params['slow_period']).mean()
        
        # Fill NaN values
        data.fillna(0, inplace=True)
        
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on moving average crossovers.
        
        Args:
            data: OHLCV data with indicators
            
        Returns:
            Series of signals (1=buy, -1=sell, 0=hold)
        """
        signals = pd.Series(0, index=data.index)
        
        # Golden cross (buy signal)
        signals[(data['sma_fast'] > data['sma_slow']) & 
                 (data['sma_fast'].shift(1) <= data['sma_slow'].shift(1))] = 1
        
        # Death cross (sell signal)
        signals[(data['sma_fast'] < data['sma_slow']) & 
                 (data['sma_fast'].shift(1) >= data['sma_slow'].shift(1))] = -1
        
        return signals
