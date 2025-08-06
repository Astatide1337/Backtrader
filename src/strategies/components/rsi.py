import pandas as pd
from .base import StrategyComponent

class RSIComponent(StrategyComponent):
    """
    RSI indicator component that adds an 'rsi' column based on the specified period.
    Uses a simple moving average of gains/losses for compatibility with existing tests.
    """

    def __init__(self, period: int = 14, price_col: str = "close", output_col: str = "rsi"):
        self.period = period
        self.price_col = price_col
        self.output_col = output_col

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        if self.price_col not in df.columns:
            raise KeyError(f"Price column '{self.price_col}' not found in data")

        delta = df[self.price_col].diff()
        gain = delta.clip(lower=0).rolling(window=self.period, min_periods=self.period).mean()
        loss = (-delta.clip(upper=0)).rolling(window=self.period, min_periods=self.period).mean()
        rs = gain / loss
        df[self.output_col] = 100 - (100 / (1 + rs))
        return df