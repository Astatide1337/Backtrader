import pandas as pd
from .base import StrategyComponent

class MovingAverageComponent(StrategyComponent):
    """
    Simple moving average component that adds an SMA column.
    Column name: sma_{period}
    """

    def __init__(self, period: int = 10, price_col: str = "close"):
        self.period = period
        self.price_col = price_col

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        sma_col = f"sma_{self.period}"
        if self.price_col not in df.columns:
            raise KeyError(f"Price column '{self.price_col}' not found in data")
        df[sma_col] = df[self.price_col].rolling(self.period).mean()
        return df