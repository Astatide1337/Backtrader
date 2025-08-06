from typing import Optional

class SizingManager:
    """Handles position sizing for trades."""
    
    def __init__(self, sizing_type: str = 'fixed_percentage', percentage: float = 0.1):
        """
        Initialize the sizing manager.
        
        Args:
            sizing_type: The type of sizing to use (e.g., 'fixed_percentage').
            percentage: The percentage of portfolio to allocate for 'fixed_percentage' sizing.
        """
        self.sizing_type = sizing_type
        self.percentage = percentage

    def calculate_quantity(self, price: float, capital: float) -> float:
        """
        Calculate the quantity for a trade based on the configured sizing strategy.
        
        Args:
            price: The current price of the asset.
            capital: The current available capital.
            
        Returns:
            The quantity to trade.
        """
        if self.sizing_type == 'fixed_percentage':
            return self._fixed_percentage_sizer(price, capital)
        else:
            # Default to a simple sizing if type is unknown
            return self._fixed_percentage_sizer(price, capital)

    def _fixed_percentage_sizer(self, price: float, capital: float) -> float:
        """
        Calculates trade quantity as a fixed percentage of the portfolio.
        
        Args:
            price: The current price of the asset.
            capital: The current available capital.
            
        Returns:
            The quantity to trade.
        """
        if price <= 0:
            return 0.0
        
        allocated_capital = capital * self.percentage
        return allocated_capital / price
