from .moving_average import MovingAverageComponent
from .rsi import RSIComponent

class IndicatorFactory:
    @staticmethod
    def create(indicator_type: str, **params):
        if indicator_type == 'sma' or indicator_type == 'ema':
            return MovingAverageComponent(indicator_type=indicator_type, **params)
        elif indicator_type == 'rsi':
            return RSIComponent(**params) # type: ignore
        else:
            raise ValueError(f"Unknown indicator type: {indicator_type}")
