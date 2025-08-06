
import os
import yaml
from typing import Dict, Any, Optional

class Config:
    """
    Centralized configuration with sensible defaults for the backtesting framework.
    """
    
    # Default configuration values
    DEFAULT_CONFIG = {
        # Backtest settings
        'initial_capital': 10000,
        'commission': 0.001,
        'slippage': 0.0005,
        
        # Data settings
        'data_source': 'yahoo_finance',
        'cache_dir': './data/cache',
        
        # Alpaca API settings
        'alpaca': {
            'api_key': 'YOUR_API_KEY',
            'secret_key': 'YOUR_SECRET_KEY',
            'paper': True,
        },

        # Strategy parameters
        'strategy_params': {},
        
        # Analysis settings
        'benchmark': 'SPY',
        'risk_free_rate': 0.02,
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration with default values and optionally load from file.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self._config = self.DEFAULT_CONFIG.copy()
        
        default_config_path = os.path.join(os.path.dirname(__file__), 'config', 'default.yaml')
        self.load_config(default_config_path)

        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """
        Load configuration from a YAML file.
        
        Args:
            config_path: Path to YAML configuration file
        """
        try:
            with open(config_path, 'r') as file:
                user_config = yaml.safe_load(file)
                if user_config:
                    self._config.update(user_config)
        except Exception as e:
            print(f"Error loading configuration from {config_path}: {e}")
    
    def save_config(self, config_path: str) -> None:
        """
        Save current configuration to a YAML file.
        
        Args:
            config_path: Path to save configuration file
        """
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as file:
                yaml.dump(self._config, file, default_flow_style=False)
        except Exception as e:
            print(f"Error saving configuration to {config_path}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration with a dictionary.
        
        Args:
            config_dict: Dictionary of configuration values
        """
        self._config.update(config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Return configuration as dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self._config.copy()
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access."""
        return self._config[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dictionary-style assignment."""
        self._config[key] = value
