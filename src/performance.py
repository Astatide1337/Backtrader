import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
import logging

class PerformanceAnalyzer:
    """Calculate and analyze performance metrics for backtest results."""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize the performance analyzer.
        
        Args:
            risk_free_rate: Annual risk-free rate (default: 2%)
        """
        self.risk_free_rate = risk_free_rate
        self.logger = logging.getLogger(__name__)
    
    def calculate_metrics(self, equity_curve: List[Dict[str, Any]], 
                         positions: List[Any], 
                         initial_capital: float) -> Dict[str, float]:
        """
        Calculate comprehensive performance metrics.
        
        Args:
            equity_curve: List of equity values over time
            positions: List of closed positions
            initial_capital: Initial capital for the backtest
            
        Returns:
            Dictionary of performance metrics
        """
        if not equity_curve:
            return {}
        
        # Convert equity curve to DataFrame
        equity_df = pd.DataFrame(equity_curve)
        equity_df.set_index('timestamp', inplace=True)
        
        # Calculate bar-to-bar returns directly from the equity curve (cash + MTM)
        # IMPORTANT: We no longer add closed position PnL to avoid double counting because equity already reflects it.
        equity_df['return'] = equity_df['equity'].pct_change()

        # Final capital equals the last equity point on the curve
        final_capital = float(equity_df['equity'].iloc[-1])

        # Calculate basic metrics from equity curve only
        total_return = (final_capital - initial_capital) / initial_capital
        
        # Annualized return (assuming 252 trading days per year)
        days = (equity_df.index[-1] - equity_df.index[0]).days
        if days > 0:
            years = days / 365.25
            # Ensure the base is non-negative before taking the root
            base = 1 + total_return
            if base < 0:
                # If base is negative, it means total loss is > 100%, return is undefined
                # Or we can take the real part of the complex number
                annualized_return = np.sign(base) * (abs(base) ** (1 / years)) - 1
            else:
                annualized_return = base ** (1 / years) - 1
        else:
            annualized_return = 0.0
        
        # Annualized volatility
        annualized_volatility = equity_df['return'].std() * np.sqrt(252)
        
        # Sharpe ratio
        if annualized_volatility > 0:
            sharpe_ratio = (annualized_return - self.risk_free_rate) / annualized_volatility
        else:
            sharpe_ratio = 0
        
        # Sortino ratio
        downside_returns = equity_df['return'][equity_df['return'] < 0]
        if len(downside_returns) > 0:
            downside_volatility = downside_returns.std() * np.sqrt(252)
            if downside_volatility > 0:
                sortino_ratio = (annualized_return - self.risk_free_rate) / downside_volatility
            else:
                sortino_ratio = 0
        else:
            sortino_ratio = 0
        
        # Maximum drawdown
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax']
        max_drawdown = equity_df['drawdown'].min()
        
        # Calmar ratio
        if max_drawdown != 0:
            calmar_ratio = annualized_return / abs(max_drawdown)
        else:
            calmar_ratio = 0
        
        # Win rate and profit factor (from positions' realized PnL; equity already includes costs)
        if positions:
            realized = [float(p.get_pnl()) for p in positions]
            winning_positions = [p for p in realized if p > 0]
            losing_positions = [p for p in realized if p <= 0]
            win_rate = (len(winning_positions) / len(realized)) if realized else 0.0
            gross_profit = sum(winning_positions) if winning_positions else 0.0
            gross_loss = abs(sum(losing_positions)) if losing_positions else 0.0
            profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf') if gross_profit > 0 else 0.0
        else:
            win_rate = 0.0
            profit_factor = 0.0
        
        # Average trade metrics (realized PnL view)
        if positions:
            realized = [float(p.get_pnl()) for p in positions]
            wins = [p for p in realized if p > 0]
            losses = [p for p in realized if p <= 0]
            avg_trade = (sum(realized) / len(realized)) if realized else 0.0
            avg_win = (sum(wins) / len(wins)) if wins else 0.0
            avg_loss = (sum(losses) / len(losses)) if losses else 0.0
        else:
            avg_trade = 0.0
            avg_win = 0.0
            avg_loss = 0.0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'annualized_volatility': annualized_volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_trade': avg_trade,
            'avg_win': avg_win,
            'avg_loss': avg_loss
        }
    
    def calculate_trade_metrics(self, positions: List[Any]) -> Dict[str, Any]:
        """
        Calculate trade-specific metrics.
        
        Args:
            positions: List of closed positions
            
        Returns:
            Dictionary of trade metrics
        """
        if not positions:
            return {}
        
        # Extract trade data
        trades = []
        for pos in positions:
            trades.append({
                'entry_time': pos.entry_time,
                'exit_time': pos.exit_time,
                'entry_price': pos.entry_price,
                'exit_price': pos.exit_price,
                'quantity': pos.quantity,
                'pnl': pos.get_pnl(),
                'return': pos.get_return(),
                'duration': (pos.exit_time - pos.entry_time).days if pos.exit_time else 0
            })
        
        trades_df = pd.DataFrame(trades)
        
        # Calculate metrics
        metrics = {
            'total_trades': len(trades),
            'winning_trades': len(trades_df[trades_df['pnl'] > 0]),
            'losing_trades': len(trades_df[trades_df['pnl'] <= 0]),
            'avg_trade_duration': trades_df['duration'].mean(),
            'max_consecutive_wins': self._calculate_max_consecutive(trades_df['pnl'] > 0),
            'max_consecutive_losses': self._calculate_max_consecutive(trades_df['pnl'] <= 0)
        }
        
        return metrics
    
    def _calculate_max_consecutive(self, series: pd.Series) -> int:
        """
        Calculate maximum consecutive True values in a series.
        
        Args:
            series: Boolean series
            
        Returns:
            Maximum consecutive True values
        """
        if series.empty:
            return 0
        
        # Create a new series that increments for each True and resets to 0 for False
        cumsum = series.cumsum()
        reset = (~series).cumsum()
        max_consecutive = (cumsum - cumsum.where(~series).ffill()).max()
        
        return int(max_consecutive) if not np.isnan(max_consecutive) else 0
    
    def generate_performance_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a text-based performance report.
        
        Args:
            results: Backtest results
            
        Returns:
            Formatted performance report
        """
        if not results:
            return "No results to report."
        
        performance = results.get('performance', {})
        positions = results.get('positions', [])
        
        # Calculate trade metrics
        trade_metrics = self.calculate_trade_metrics(positions)
        
        # Format report
        report = f"""
=== BACKTEST PERFORMANCE REPORT ===

Strategy: {results.get('strategy', 'N/A')}
Symbol: {results.get('symbol', 'N/A')}
Period: {results.get('start_date', 'N/A')} to {results.get('end_date', 'N/A')}

=== CAPITAL ===
Initial Capital: ${results.get('initial_capital', 0):.2f}
Final Capital: ${results.get('final_capital', 0):.2f}
Total Return: {performance.get('total_return', 0) * 100:.2f}%
Annualized Return: {performance.get('annualized_return', 0) * 100:.2f}%

=== RISK METRICS ===
Annualized Volatility: {performance.get('annualized_volatility', 0) * 100:.2f}%
Sharpe Ratio: {performance.get('sharpe_ratio', 0):.2f}
Sortino Ratio: {performance.get('sortino_ratio', 0):.2f}
Calmar Ratio: {performance.get('calmar_ratio', 0):.2f}
Max Drawdown: {performance.get('max_drawdown', 0) * 100:.2f}%

=== TRADE METRICS ===
Total Trades: {trade_metrics.get('total_trades', 0)}
Winning Trades: {trade_metrics.get('winning_trades', 0)}
Losing Trades: {trade_metrics.get('losing_trades', 0)}
Win Rate: {performance.get('win_rate', 0) * 100:.2f}%
Profit Factor: {performance.get('profit_factor', 0):.2f}
Avg Trade: ${performance.get('avg_trade', 0):.2f}
Avg Win: ${performance.get('avg_win', 0):.2f}
Avg Loss: ${performance.get('avg_loss', 0):.2f}
Avg Trade Duration: {trade_metrics.get('avg_trade_duration', 0):.1f} days
Max Consecutive Wins: {trade_metrics.get('max_consecutive_wins', 0)}
Max Consecutive Losses: {trade_metrics.get('max_consecutive_losses', 0)}
"""
        return report