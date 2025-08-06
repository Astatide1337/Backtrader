
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from .components.base import StrategyComponent

class Strategy(ABC):
    """
    Abstract base class for all trading strategies.
    """
    
    def __init__(self, components: Optional[List[StrategyComponent]] = None, **params):
        """
        Initialize the strategy with parameters and components.
        
        Args:
            components: A list of strategy components.
            **params: Strategy parameters
        """
        self.components = components or []
        self.params = params
        self.name = self.__class__.__name__
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate required indicators for the strategy.
        
        Args:
            data: OHLCV data
            
        Returns:
            DataFrame with added indicator columns
        """
        for component in self.components:
            data = component.calculate(data)
        return data
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals (1=buy, -1=sell, 0=hold).
        
        Args:
            data: OHLCV data with indicators
            
        Returns:
            Series of signals
        """
        pass
    
    def get_name(self) -> str:
        """
        Return strategy name.
        
        Returns:
            Strategy name
        """
        return self.name
    
    def get_params(self) -> Dict[str, Any]:
        """
        Return strategy parameters.
        
        Returns:
            Dictionary of parameters
        """
        return self.params
    
    def set_params(self, **params) -> None:
        """
        Set strategy parameters.
        
        Args:
            **params: Parameters to set
        """
        self.params.update(params)
