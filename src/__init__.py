"""
Backtesting Framework - A streamlined backtesting framework for trading strategies.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .config import Config
from .data_manager import DataManager
from .strategy_manager import StrategyManager
from .order_manager import OrderManager, Order, Position, OrderType, OrderStatus, OrderDirection
from .engine import BacktestEngine
from .performance import PerformanceAnalyzer
from .optimizer import BasicOptimizer
from .plotting import Plotter

__all__ = [
    "Config", 
    "DataManager", 
    "StrategyManager", 
    "OrderManager", 
    "Order", 
    "Position", 
    "OrderType", 
    "OrderStatus", 
    "OrderDirection",
    "BacktestEngine",
    "PerformanceAnalyzer",
    "BasicOptimizer",
    "Plotter"
]