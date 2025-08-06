"""
Parameter optimization example.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.config import Config
from src.optimizer import BasicOptimizer
from src.performance import PerformanceAnalyzer
from src.plotting import Plotter
import asyncio

async def main():
    """Run a parameter optimization example."""
    print("=== Parameter Optimization Example ===")
    
    # Initialize configuration
    config = Config()
    config.set('initial_capital', 10000)
    config.set('commission', 0.001)
    config.set('slippage', 0.0005)
    
    # Create optimizer
    optimizer = BasicOptimizer(config)
    
    # Define parameter grid for Moving Average Crossover strategy
    param_grid = {
        'fast_period': [5, 10, 15, 20],
        'slow_period': [20, 30, 40, 50],
        'stop_loss_pct': [2, 3, 5],
        'take_profit_pct': [5, 8, 10]
    }
    
    print(f"\nOptimizing Moving Average Crossover strategy with {len(param_grid['fast_period']) * len(param_grid['slow_period']) * len(param_grid['stop_loss_pct']) * len(param_grid['take_profit_pct'])} parameter combinations...")
    
    # Run optimization
    optimization_results = await optimizer.grid_search(
        strategy_name='moving_average_crossover',
        symbol='AAPL',
        start_date='2022-01-01',
        end_date='2022-12-31',
        param_grid=param_grid
    )
    
    # Print best parameters
    best_params = optimization_results['best_params']
    best_score = optimization_results['best_score']
    best_metrics = optimization_results['best_metrics']
    
    print(f"\nBest Parameters:")
    for param, value in best_params.items():
        print(f"  {param}: {value}")
    
    print(f"\nBest Sharpe Ratio: {best_score:.2f}")
    
    print(f"\nPerformance with Best Parameters:")
    print(f"Total Return: {best_metrics['total_return']:.2%}")
    print(f"Annualized Return: {best_metrics['annualized_return']:.2%}")
    print(f"Max Drawdown: {best_metrics['max_drawdown']:.2%}")
    print(f"Win Rate: {best_metrics['win_rate']:.2%}")
    print(f"Profit Factor: {best_metrics['profit_factor']:.2f}")
    
    # Generate optimization report
    print("\n=== Optimization Report ===")
    report = optimizer.generate_optimization_report(optimization_results)
    print(report)
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Plot parameter heatmap
    print("\nGenerating parameter heatmap...")
    plotter = Plotter()
    
    # Plot heatmap for fast_period vs slow_period
    plotter.plot_parameter_heatmap( # type: ignore
        optimization_results,
        param_x='fast_period',
        param_y='slow_period',
        title="Sharpe Ratio by Fast Period vs Slow Period",
        save_path='output/parameter_heatmap_fast_slow.png'
    )
    
    # Plot heatmap for stop_loss_pct vs take_profit_pct
    plotter.plot_parameter_heatmap( # type: ignore
        optimization_results,
        param_x='stop_loss_pct',
        param_y='take_profit_pct',
        title="Sharpe Ratio by Stop Loss vs Take Profit",
        save_path='output/parameter_heatmap_stop_take.png'
    )
    
    print("\nParameter heatmaps saved to output/ directory")
    
    # Run backtest with best parameters
    print("\n=== Running backtest with best parameters ===")
    from engine import BacktestEngine
    engine = BacktestEngine(config)
    
    results = await engine.run_backtest(
        strategy_name='moving_average_crossover',
        symbols=['AAPL'],
        start_date='2022-01-01',
        end_date='2022-12-31',
        **best_params
    )
    
    # Plot results
    print("\nGenerating plots for best parameters...")
    
    # Plot equity curve
    plotter.plot_equity_curve(
        results['equity_curve'],
        title=f"Equity Curve - Optimized Parameters - {results['symbol']}",
        save_path='output/optimized_equity_curve.png'
    )
    
    # Plot drawdown
    plotter.plot_drawdown(
        results['equity_curve'],
        title=f"Drawdown - Optimized Parameters - {results['symbol']}",
        save_path='output/optimized_drawdown.png'
    )
    
    
    print("\nPlots saved to output/ directory")
    print("\nExample completed successfully!")

if __name__ == '__main__':
    asyncio.run(main())