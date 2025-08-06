"""
Custom strategy implementation example.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from strategies.base import Strategy
from config import Config
from engine import BacktestEngine
from strategy_manager import StrategyManager
from performance import PerformanceAnalyzer
from plotting import Plotter

class BollingerBandsStrategy(Strategy):
    """
    Bollinger Bands strategy.
    
    Generates buy signals when the price crosses below the lower Bollinger Band,
    and sell signals when the price crosses above the upper Bollinger Band.
    """
    
    def __init__(self, period=20, std_dev=2, stop_loss_pct=3, take_profit_pct=8):
        """
        Initialize the strategy.
        
        Args:
            period: Period for Bollinger Bands calculation
            std_dev: Number of standard deviations for the bands
            stop_loss_pct: Stop loss percentage
            take_profit_pct: Take profit percentage
        """
        super().__init__(
            period=period,
            std_dev=std_dev,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct
        )
    
    def calculate_indicators(self, data):
        """
        Calculate the Bollinger Bands indicators.
        
        Args:
            data: OHLCV data
            
        Returns:
            DataFrame with added indicator columns
        """
        data = data.copy()
        
        # Calculate middle band (simple moving average)
        data['middle_band'] = data['close'].rolling(window=self.params['period']).mean()
        
        # Calculate standard deviation
        data['std_dev'] = data['close'].rolling(window=self.params['period']).std()
        
        # Calculate upper and lower bands
        data['upper_band'] = data['middle_band'] + (data['std_dev'] * self.params['std_dev'])
        data['lower_band'] = data['middle_band'] - (data['std_dev'] * self.params['std_dev'])
        
        # Calculate bandwidth and %b
        data['bandwidth'] = (data['upper_band'] - data['lower_band']) / data['middle_band']
        data['percent_b'] = (data['close'] - data['lower_band']) / (data['upper_band'] - data['lower_band'])
        
        return data
    
    def generate_signals(self, data):
        """
        Generate trading signals based on Bollinger Bands.
        
        Args:
            data: OHLCV data with indicators
            
        Returns:
            Series of signals (1=buy, -1=sell, 0=hold)
        """
        signals = pd.Series(0, index=data.index)
        
        # Buy signal when price crosses below lower band
        signals[(data['close'] < data['lower_band']) & 
                 (data['close'].shift(1) >= data['lower_band'].shift(1))] = 1
        
        # Sell signal when price crosses above upper band
        signals[(data['close'] > data['upper_band']) & 
                 (data['close'].shift(1) <= data['upper_band'].shift(1))] = -1
        
        return signals
    
    def get_name(self):
        """Return strategy name."""
        return "BollingerBandsStrategy"

def main():
    """Run a custom strategy example."""
    print("=== Custom Strategy Example ===")
    
    # Initialize configuration
    config = Config()
    config.set('initial_capital', 10000)
    config.set('commission', 0.001)
    config.set('slippage', 0.0005)
    
    # Create strategy manager
    strategy_manager = StrategyManager()
    
    # Register custom strategy
    strategy_manager.register_strategy('bollinger_bands', BollingerBandsStrategy)
    
    # Create backtest engine with custom strategy manager
    engine = BacktestEngine(config, strategy_manager)
    
    # Run backtest with custom strategy
    print("\nRunning backtest with Bollinger Bands strategy...")
    results = engine.run_backtest(
        strategy_name='bollinger_bands',
        symbol='AAPL',
        start_date='2022-01-01',
        end_date='2022-12-31',
        period=20,
        std_dev=2,
        stop_loss_pct=3,
        take_profit_pct=8
    )
    
    # Print basic results
    print(f"\nStrategy: {results['strategy']}")
    print(f"Symbol: {results['symbol']}")
    print(f"Period: {results['start_date']} to {results['end_date']}")
    print(f"Initial Capital: ${results['initial_capital']:.2f}")
    print(f"Final Capital: ${results['final_capital']:.2f}")
    
    # Print performance metrics
    performance = results['performance']
    print(f"\nPerformance Metrics:")
    print(f"Total Return: {performance['total_return']:.2%}")
    print(f"Annualized Return: {performance['annualized_return']:.2%}")
    print(f"Sharpe Ratio: {performance['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {performance['max_drawdown']:.2%}")
    print(f"Win Rate: {performance['win_rate']:.2%}")
    print(f"Profit Factor: {performance['profit_factor']:.2f}")
    
    # Print trade metrics
    positions = results['positions']
    print(f"\nTrade Metrics:")
    print(f"Total Trades: {len(positions)}")
    winning_trades = [p for p in positions if p.get_pnl() > 0]
    losing_trades = [p for p in positions if p.get_pnl() <= 0]
    print(f"Winning Trades: {len(winning_trades)}")
    print(f"Losing Trades: {len(losing_trades)}")
    
    # Generate detailed performance report
    print("\n=== Performance Report ===")
    analyzer = PerformanceAnalyzer()
    report = analyzer.generate_performance_report(results)
    print(report)
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Plot results
    print("\nGenerating plots...")
    plotter = Plotter()
    
    # Plot equity curve
    plotter.plot_equity_curve(
        results['equity_curve'],
        title=f"Equity Curve - {results['strategy']} - {results['symbol']}",
        save_path='output/custom_equity_curve.png'
    )
    
    # Plot drawdown
    plotter.plot_drawdown(
        results['equity_curve'],
        title=f"Drawdown - {results['strategy']} - {results['symbol']}",
        save_path='output/custom_drawdown.png'
    )
    
    
    print("\nPlots saved to output/ directory")
    
    # Optimize custom strategy parameters
    print("\n=== Optimizing custom strategy parameters ===")
    from optimizer import BasicOptimizer
    
    optimizer = BasicOptimizer(config, strategy_manager=strategy_manager)
    
    # Define parameter grid
    param_grid = {
        'period': [10, 20, 30],
        'std_dev': [1.5, 2, 2.5],
        'stop_loss_pct': [2, 3, 5],
        'take_profit_pct': [5, 8, 10]
    }
    
    print(f"Optimizing with {len(param_grid['period']) * len(param_grid['std_dev']) * len(param_grid['stop_loss_pct']) * len(param_grid['take_profit_pct'])} parameter combinations...")
    
    # Run optimization
    optimization_results = optimizer.grid_search(
        strategy_name='bollinger_bands',
        symbol='AAPL',
        start_date='2022-01-01',
        end_date='2022-12-31',
        param_grid=param_grid
    )
    
    # Print best parameters
    best_params = optimization_results['best_params']
    best_score = optimization_results['best_score']
    
    print(f"\nBest Parameters:")
    for param, value in best_params.items():
        print(f"  {param}: {value}")
    
    print(f"\nBest Sharpe Ratio: {best_score:.2f}")
    
    # Run backtest with optimized parameters
    print("\n=== Running backtest with optimized parameters ===")
    optimized_results = engine.run_backtest(
        strategy_name='bollinger_bands',
        symbol='AAPL',
        start_date='2022-01-01',
        end_date='2022-12-31',
        **best_params
    )
    
    # Compare performance
    print("\n=== Performance Comparison ===")
    print(f"Original Total Return: {performance['total_return']:.2%}")
    print(f"Optimized Total Return: {optimized_results['performance']['total_return']:.2%}")
    print(f"Original Sharpe Ratio: {performance['sharpe_ratio']:.2f}")
    print(f"Optimized Sharpe Ratio: {optimized_results['performance']['sharpe_ratio']:.2f}")
    print(f"Original Max Drawdown: {performance['max_drawdown']:.2%}")
    print(f"Optimized Max Drawdown: {optimized_results['performance']['max_drawdown']:.2%}")
    
    # Plot optimized results
    print("\nGenerating plots for optimized parameters...")
    
    # Plot equity curve
    plotter.plot_equity_curve(
        optimized_results['equity_curve'],
        title=f"Equity Curve - Optimized Bollinger Bands - {results['symbol']}",
        save_path='output/optimized_custom_equity_curve.png'
    )
    
    # Plot drawdown
    plotter.plot_drawdown(
        optimized_results['equity_curve'],
        title=f"Drawdown - Optimized Bollinger Bands - {results['symbol']}",
        save_path='output/optimized_custom_drawdown.png'
    )
    
    print("\nPlots saved to output/ directory")
    print("\nExample completed successfully!")

if __name__ == '__main__':
    main()