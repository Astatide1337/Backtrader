import pandas as pd
from .base import StrategyComponent
from typing import Optional

class MovingAverageComponent(StrategyComponent):
    """
    Moving average component that adds an SMA or EMA column.
    """

    def __init__(self, period: int = 10, price_col: str = "close", indicator_type: str = "sma", output_col: Optional[str] = None):
        self.period = period
        self.price_col = price_col
        self.indicator_type = indicator_type
        self.output_col = output_col or f"{indicator_type}_{self.period}"

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        if self.price_col not in df.columns:
            raise KeyError(f"Price column '{self.price_col}' not found in data")
        
        if self.indicator_type == "sma":
            df[self.output_col] = df[self.price_col].rolling(self.period).mean()
        elif self.indicator_type == "ema":
            df[self.output_col] = df[self.price_col].ewm(span=self.period, adjust=False).mean()
        else:
            raise ValueError(f"Unsupported indicator type: {self.indicator_type}")
            
        return df

    def get_column_name(self) -> str:
        return self.output_col
