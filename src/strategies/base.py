
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


class ComposableStrategy(Strategy):
    """
    A strategy that is composed of indicators and rules defined in a dictionary.
    """
    def __init__(self, definition: Dict[str, Any]):
        super().__init__()
        self.definition = definition
        self.name = definition.get('basics', {}).get('name', 'ComposableStrategy')
        self.indicator_map: Dict[str, str] = {}

    @classmethod
    def from_dict(cls, definition: Dict[str, Any]) -> 'ComposableStrategy':
        return cls(definition)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        from .components.factory import IndicatorFactory
        
        for indicator_def in self.definition.get('indicators', []):
            params_list = indicator_def.get('params', [])
            params_dict = {p['key']: p['value'] for p in params_list}
            indicator = IndicatorFactory.create(indicator_def['type'], **params_dict)
            data = indicator.calculate(data)
            # Map the user-defined ID to the generated column name
            self.indicator_map[indicator_def['id']] = indicator.get_column_name()
        return data

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(index=data.index, data=0)
        
        entry_rules = self.definition.get('entry', {})
        if entry_rules:
            entry_signals = self._evaluate_rule_group(entry_rules.get('groups', []), data)
            signals[entry_signals] = 1

        exit_rules = self.definition.get('exit', {})
        if exit_rules:
            exit_signals = self._evaluate_rule_group(exit_rules.get('groups', []), data)
            signals[exit_signals] = -1
            
        return signals

    def _evaluate_rule_group(self, groups: List[Dict[str, Any]], data: pd.DataFrame) -> pd.Series:
        final_mask = pd.Series(index=data.index, data=False)

        for group in groups:
            group_mask = self._evaluate_group(group, data)
            final_mask = final_mask | group_mask
            
        return final_mask

    def _evaluate_group(self, group: Dict[str, Any], data: pd.DataFrame) -> pd.Series:
        op = group.get('op', 'AND').upper()
        
        if not group.get('conditions'):
            return pd.Series(index=data.index, data=False)

        condition_masks = [self._evaluate_condition(c, data) for c in group['conditions']]
        
        if not condition_masks:
            return pd.Series(index=data.index, data=False)

        if op == 'AND':
            combined_mask = pd.concat(condition_masks, axis=1).all(axis=1)
        elif op == 'OR':
            combined_mask = pd.concat(condition_masks, axis=1).any(axis=1)
        else:
            raise ValueError(f"Unsupported group operator: {op}")
            
        return combined_mask

    def _evaluate_condition(self, condition: Dict[str, Any], data: pd.DataFrame) -> pd.Series:
        left = self._get_operand_value(condition['left'], data)
        right = self._get_operand_value(condition['right'], data)
        op = condition['op']

        if op == 'gt':
            return left > right
        elif op == 'lt':
            return left < right
        elif op == 'eq':
            return left == right
        # Add more operators as needed
        else:
            raise ValueError(f"Unsupported operator: {op}")

    def _get_operand_value(self, operand: Dict[str, Any], data: pd.DataFrame) -> Any:
        kind = operand.get('kind')
        if kind == 'indicator':
            ref = operand.get('ref')
            column_name = self.indicator_map.get(ref)
            if not column_name or column_name not in data.columns:
                raise ValueError(f"Indicator '{ref}' not found in data columns")
            return data[column_name]
        elif kind == 'value':
            return operand.get('value')
        else:
            raise ValueError(f"Unsupported operand kind: {kind}")
