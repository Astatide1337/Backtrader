from abc import ABC, abstractmethod
import pandas as pd

class StrategyComponent(ABC):
    """
    Base class for modular strategy components (indicators, filters, signals).
    Components transform the input DataFrame by adding columns or filtering rows.
    """

    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply the component's transformation to the data and return the modified DataFrame.
        Implementations should avoid mutating the input DataFrame in place; copy if needed.
        """
        raise NotImplementedError

    @abstractmethod
    def get_column_name(self) -> str:
        """
        Return the name of the column this component adds.
        """
        raise NotImplementedError


class NoOpComponent(StrategyComponent):
    """
    No-op component that returns the data unchanged.
    Useful as a placeholder when composing strategies without extra components.
    """

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        return data