import pandas as pd
from typing import Dict, Type, Any, Optional
from src.strategies.base import Strategy
from src.strategies.moving_average import MovingAverageCrossover
from src.strategies.rsi_mean_reversion import RSIMeanReversion
from src.strategies.macd import MACDStrategy

class StrategyManager:
    """
    Manage and execute trading strategies.
    """
    
    # Registry of available strategies
    STRATEGIES: Dict[str, Type[Strategy]] = {
        'moving_average_crossover': MovingAverageCrossover,
        'rsi_mean_reversion': RSIMeanReversion,
        'macd': MACDStrategy,
    }
    
    def __init__(self):
        """Initialize the strategy manager."""
        self.registered_strategies = self.STRATEGIES.copy()
    
    def register_strategy(self, name: str, strategy_class: Type[Strategy]) -> None:
        """
        Register a custom strategy.
        
        Args:
            name: Name to register the strategy under
            strategy_class: Strategy class to register
        """
        self.registered_strategies[name] = strategy_class
    
    def create_strategy(self, name: str, **params) -> Optional[Strategy]:
        """
        Create a strategy instance.
        
        Args:
            name: Name of the strategy
            **params: Parameters to pass to the strategy
            
        Returns:
            Strategy instance or None if not found
        """
        if name not in self.registered_strategies:
            return None
        
        strategy_class = self.registered_strategies[name]
        return strategy_class(**params)
    
    def list_strategies(self) -> Dict[str, Type[Strategy]]:
        """
        List all available strategies.
        
        Returns:
            Dictionary of strategy names and classes
        """
        return self.registered_strategies.copy()
    
    def run_strategy(self, strategy: Strategy, data: pd.DataFrame) -> pd.DataFrame:
        """
        Run a strategy on the provided data.
        
        Args:
            strategy: Strategy instance to run
            data: OHLCV data
            
        Returns:
            DataFrame with signals and indicators
        """
        # Calculate indicators
        data_with_indicators = strategy.calculate_indicators(data)
        
        # Generate signals
        signals = strategy.generate_signals(data_with_indicators)
        
        # Add signals to the data
        result = data_with_indicators.copy()
        result['signal'] = signals
        
        return result