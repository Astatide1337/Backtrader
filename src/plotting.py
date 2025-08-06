import pandas as pd
import numpy as np
import matplotlib
# Use a non-interactive backend for headless/test environments
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
import logging

class Plotter:
    """Basic plotting functionality for backtest results."""
    
    def __init__(self, figsize: Tuple[int, int] = (12, 8), style: str = 'seaborn-v0_8'):
        """
        Initialize the plotter.
        
        Args:
            figsize: Figure size (default: (12, 8))
            style: Matplotlib style (default: 'seaborn-v0_8')
        """
        self.figsize = figsize
        self.style = style
        self.logger = logging.getLogger(__name__)
        
        # Set matplotlib style
        try:
            plt.style.use(style)
        except:
            self.logger.warning(f"Style '{style}' not available, using default style")
    
    def plot_equity_curve(self, equity_curve: List[Dict[str, Any]], 
                         title: str = "Equity Curve", 
                         save_path: Optional[str] = None,
                         show_trades: bool = False,
                         positions: Optional[List[Any]] = None) -> Optional[plt.Figure]: # type: ignore
        """
        Plot the equity curve.
        
        Args:
            equity_curve: List of equity values over time
            title: Plot title
            save_path: Path to save the plot
            show_trades: Whether to show trade entry/exit points
            positions: List of positions (required if show_trades is True)
        """
        if not equity_curve:
            self.logger.error("No equity curve data to plot")
            return
        
        # Convert equity curve to DataFrame
        equity_df = pd.DataFrame(equity_curve)
        equity_df.set_index('timestamp', inplace=True)
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot equity curve
        ax.plot(equity_df.index, equity_df['equity'], label='Portfolio Value', color='blue', linewidth=2)
        
        # Add trade markers if requested
        if show_trades and positions:
            for pos in positions:
                if pos.entry_time and pos.exit_time:
                    # Entry point
                    entry_equity = equity_df.loc[pos.entry_time, 'equity'] if pos.entry_time in equity_df.index else None
                    if entry_equity is not None:
                        ax.plot(pos.entry_time, entry_equity, 'go' if pos.quantity > 0 else 'ro',  # type: ignore
                               markersize=8, label='Entry' if 'Entry' not in [l.get_label() for l in ax.get_legend_handles_labels()[0]] else "")
                    
                    # Exit point
                    exit_equity = equity_df.loc[pos.exit_time, 'equity'] if pos.exit_time in equity_df.index else None
                    if exit_equity is not None:
                        ax.plot(pos.exit_time, exit_equity, 'rx' if pos.quantity > 0 else 'gx',  # type: ignore
                               markersize=8, label='Exit' if 'Exit' not in [l.get_label() for l in ax.get_legend_handles_labels()[0]] else "")
        
        # Format plot
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Portfolio Value ($)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # Save plot if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Equity curve plot saved to {save_path}")
        
        plt.show()
        return fig
    
    def plot_drawdown(self, equity_curve: List[Dict[str, Any]], 
                     title: str = "Drawdown", 
                     save_path: Optional[str] = None) -> Optional[plt.Figure]: # type: ignore
        """
        Plot the drawdown.
        
        Args:
            equity_curve: List of equity values over time
            title: Plot title
            save_path: Path to save the plot
        """
        if not equity_curve:
            self.logger.error("No equity curve data to plot drawdown")
            return
        
        # Convert equity curve to DataFrame
        equity_df = pd.DataFrame(equity_curve)
        equity_df.set_index('timestamp', inplace=True)
        
        # Calculate drawdown
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax'] * 100
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot drawdown
        ax.fill_between(equity_df.index, equity_df['drawdown'], 0, color='red', alpha=0.3)
        ax.plot(equity_df.index, equity_df['drawdown'], color='red', linewidth=1)
        
        # Format plot
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Drawdown (%)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # Save plot if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Drawdown plot saved to {save_path}")
        
        plt.show()
        return fig
    
    def plot_trades(self, data: pd.DataFrame, 
                   positions: List[Any], 
                   title: str = "Trades", 
                   save_path: Optional[str] = None) -> None:
        """
        Plot trades on price chart.
        
        Args:
            data: OHLCV data
            positions: List of positions
            title: Plot title
            save_path: Path to save the plot
        """
        if not positions:
            self.logger.warning("No positions to plot")
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot price
        ax.plot(data.index, data['close'], label='Price', color='black', linewidth=1)
        
        # Plot trades
        for pos in positions:
            if pos.entry_time and pos.exit_time:
                # Entry point
                if pos.entry_time in data.index:
                    entry_price = data.loc[pos.entry_time, 'close']
                    ax.plot(pos.entry_time, entry_price, 'go' if pos.quantity > 0 else 'ro',  # type: ignore
                           markersize=10, label='Buy' if pos.quantity > 0 else 'Sell' if 'Buy' not in [l.get_label() for l in ax.get_legend_handles_labels()[0]] and 'Sell' not in [l.get_label() for l in ax.get_legend_handles_labels()[0]] else "")
                
                # Exit point
                if pos.exit_time in data.index:
                    exit_price = data.loc[pos.exit_time, 'close']
                    ax.plot(pos.exit_time, exit_price, 'rx' if pos.quantity > 0 else 'gx',  # type: ignore
                           markersize=10, label='Sell' if pos.quantity > 0 else 'Buy' if 'Sell' not in [l.get_label() for l in ax.get_legend_handles_labels()[0]] and 'Buy' not in [l.get_label() for l in ax.get_legend_handles_labels()[0]] else "")
                
                # Draw line between entry and exit
                if pos.entry_time in data.index and pos.exit_time in data.index:
                    entry_price = data.loc[pos.entry_time, 'close']
                    exit_price = data.loc[pos.exit_time, 'close']
                    ax.plot([pos.entry_time, pos.exit_time], [entry_price, exit_price],  # type: ignore
                           'g-' if pos.quantity > 0 else 'r-', alpha=0.5)
        
        # Format plot
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price ($)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # Save plot if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Trades plot saved to {save_path}")
        
        plt.show()
    
    def plot_monthly_returns(self, equity_curve: List[Dict[str, Any]], 
                            title: str = "Monthly Returns", 
                            save_path: Optional[str] = None) -> Optional[plt.Figure]: # type: ignore
        """
        Plot monthly returns heatmap.
        
        Args:
            equity_curve: List of equity values over time
            title: Plot title
            save_path: Path to save the plot
        """
        if not equity_curve:
            self.logger.error("No equity curve data to plot monthly returns")
            return
        
        # Convert equity curve to DataFrame
        equity_df = pd.DataFrame(equity_curve)
        equity_df.set_index('timestamp', inplace=True)
        
        # Calculate daily returns
        equity_df['return'] = equity_df['equity'].pct_change()
        
        # Resample to monthly returns
        monthly_returns = equity_df['return'].resample('M').apply(lambda x: (1 + x).prod() - 1)
        
        # Create pivot table for heatmap
        monthly_returns_df = monthly_returns.to_frame() # type: ignore
        monthly_returns_df = monthly_returns_df.reset_index()
        monthly_returns_df['year'] = monthly_returns_df['timestamp'].dt.year
        monthly_returns_df['month'] = monthly_returns_df['timestamp'].dt.month
        pivot_table = monthly_returns_df.pivot_table(index='year', columns='month', values='return')
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot heatmap
        cmap = plt.cm.RdYlGn # type: ignore
        im = ax.pcolormesh(pivot_table.columns, pivot_table.index, pivot_table.values, 
                          cmap=cmap, vmin=-0.1, vmax=0.1)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Monthly Return', fontsize=12)
        
        # Format plot
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Year', fontsize=12)
        
        # Set ticks - match the actual columns and rows
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Set ticks based on actual pivot table structure
        ax.set_xticks(pivot_table.columns)
        ax.set_yticks(pivot_table.index)
        
        # Set labels for months (only for available months)
        x_labels = [month_names[m-1] if m <= 12 else str(m) for m in pivot_table.columns] # type: ignore
        ax.set_xticklabels(x_labels)
        ax.set_yticklabels(pivot_table.index)
        
        # Add text annotations
        for i in range(len(pivot_table.index)):
            for j in range(len(pivot_table.columns)):
                value = pivot_table.iloc[i, j]
                if isinstance(value, (int, float)) and not np.isnan(value):
                    ax.text(j + 0.5, i + 0.5, f'{value:.1%}', 
                           ha='center', va='center', color='black' if abs(value) < 0.05 else 'white')
        
        plt.tight_layout()
        
        # Save plot if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Monthly returns plot saved to {save_path}")
        
        plt.show()
        return fig
    
    def plot_rolling_metrics(self, equity_curve: List[Dict[str, Any]], 
                           window: int = 30, 
                           title: str = "Rolling Metrics", 
                           save_path: Optional[str] = None) -> None:
        """
        Plot rolling metrics.
        
        Args:
            equity_curve: List of equity values over time
            window: Rolling window in days
            title: Plot title
            save_path: Path to save the plot
        """
        if not equity_curve:
            self.logger.error("No equity curve data to plot rolling metrics")
            return
        
        # Convert equity curve to DataFrame
        equity_df = pd.DataFrame(equity_curve)
        equity_df.set_index('timestamp', inplace=True)
        
        # Calculate daily returns
        equity_df['return'] = equity_df['equity'].pct_change()
        
        # Calculate rolling metrics
        equity_df['rolling_return'] = equity_df['return'].rolling(window=window).apply(lambda x: (1 + x).prod() - 1)
        equity_df['rolling_volatility'] = equity_df['return'].rolling(window=window).std() * np.sqrt(252)
        equity_df['rolling_sharpe'] = equity_df['rolling_return'] / equity_df['rolling_volatility']
        
        # Create figure with subplots
        fig, axes = plt.subplots(3, 1, figsize=self.figsize, sharex=True)
        
        # Plot rolling return
        axes[0].plot(equity_df.index, equity_df['rolling_return'], label='Rolling Return', color='blue')
        axes[0].set_title(f'Rolling {window}-Day Return', fontsize=12)
        axes[0].set_ylabel('Return', fontsize=10)
        axes[0].grid(True, alpha=0.3)
        
        # Plot rolling volatility
        axes[1].plot(equity_df.index, equity_df['rolling_volatility'], label='Rolling Volatility', color='red')
        axes[1].set_title(f'Rolling {window}-Day Volatility', fontsize=12)
        axes[1].set_ylabel('Volatility', fontsize=10)
        axes[1].grid(True, alpha=0.3)
        
        # Plot rolling Sharpe ratio
        axes[2].plot(equity_df.index, equity_df['rolling_sharpe'], label='Rolling Sharpe Ratio', color='green')
        axes[2].set_title(f'Rolling {window}-Day Sharpe Ratio', fontsize=12)
        axes[2].set_ylabel('Sharpe Ratio', fontsize=10)
        axes[2].set_xlabel('Date', fontsize=10)
        axes[2].grid(True, alpha=0.3)
        
        # Format x-axis
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            plt.setp(ax.get_xticklabels(), rotation=45)
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        # Save plot if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Rolling metrics plot saved to {save_path}")
        
        plt.show()
    
    def plot_parameter_heatmap(self, optimization_results: Dict[str, Any], 
                              param_x: str, param_y: str, 
                              title: str = "Parameter Heatmap", 
                              save_path: Optional[str] = None) -> None:
        """
        Plot parameter optimization results as a heatmap.
        
        Args:
            optimization_results: Results from optimization
            param_x: Parameter name for x-axis
            param_y: Parameter name for y-axis
            title: Plot title
            save_path: Path to save the plot
        """
        all_results = optimization_results.get('all_results', [])
        
        if not all_results:
            self.logger.error("No optimization results to plot")
            return
        
        # Extract parameter values and scores
        param_x_values = []
        param_y_values = []
        scores = []
        
        for result in all_results:
            params = result.get('params', {})
            if param_x in params and param_y in params:
                param_x_values.append(params[param_x])
                param_y_values.append(params[param_y])
                scores.append(result.get('score', 0))
        
        # Create DataFrame
        df = pd.DataFrame({
            param_x: param_x_values,
            param_y: param_y_values,
            'score': scores
        })
        
        # Create pivot table for heatmap
        pivot_table = df.pivot_table(index=param_y, columns=param_x, values='score')
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot heatmap
        im = ax.pcolormesh(pivot_table.columns, pivot_table.index, pivot_table.values, 
                          cmap='viridis')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Score', fontsize=12)
        
        # Format plot
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(param_x, fontsize=12)
        ax.set_ylabel(param_y, fontsize=12)
        
        # Set ticks
        ax.set_xticks(np.arange(0.5, len(pivot_table.columns), 1))
        ax.set_yticks(np.arange(0.5, len(pivot_table.index), 1))
        ax.set_xticklabels(pivot_table.columns)
        ax.set_yticklabels(pivot_table.index)
        
        # Add text annotations
        for i in range(len(pivot_table.index)):
            for j in range(len(pivot_table.columns)):
                value = pivot_table.iloc[i, j]
                if isinstance(value, (int, float)) and not np.isnan(value):
                    ax.text(j + 0.5, i + 0.5, f'{value:.2f}', 
                           ha='center', va='center', color='white')
        
        plt.tight_layout()
        
        # Save plot if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Parameter heatmap plot saved to {save_path}")
        
        plt.show()