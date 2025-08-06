"""
Strategy module for the backtesting framework.
"""

from .base import Strategy
from .moving_average import MovingAverageCrossover
from .rsi_mean_reversion import RSIMeanReversion
from .macd import MACDStrategy

__all__ = ["Strategy", "MovingAverageCrossover", "RSIMeanReversion", "MACDStrategy"]