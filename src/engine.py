import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging

from src.config import Config
from src.data_manager import DataManager
from src.strategy_manager import StrategyManager
from src.order_manager import OrderManager, OrderType, OrderDirection
from src.sizing_manager import SizingManager

class BacktestEngine:
    """Main backtesting engine."""
    
    def __init__(self, config: Optional[Config] = None, strategy_manager: Optional[StrategyManager] = None):
        """
        Initialize the backtesting engine.
        """
        self.config = config or Config()
        self.data_manager = DataManager(cache_dir=self.config.get('cache_dir', './data/cache'))
        self.strategy_manager = strategy_manager or StrategyManager()
        self.order_manager = OrderManager(
            commission=self.config.get('commission', 0.001),
            slippage=self.config.get('slippage', 0.0005)
        )
        self.sizing_manager = SizingManager(
            sizing_type=self.config.get('sizing_type', 'fixed_percentage'),
            percentage=self.config.get('sizing_percentage', 0.1)
        )
        self.logger = logging.getLogger(__name__)
        self.initial_capital = self.config.get('initial_capital', 10000)
        self.equity_curve = []
        
    async def run_backtest(self, strategy_name: str, symbols: Union[str, List[str]], start_date: Union[str, datetime], 
                     end_date: Union[str, datetime], **strategy_params) -> Dict[str, Any]:
        """
        Run a backtest on one or more symbols.
        """
        self._reset_state()
        
        data_dict = self.data_manager.fetch_data(symbols, start_date, end_date)
        if not data_dict or all(df.empty for df in data_dict.values()):
            self.logger.error(f"No data found for symbols: {symbols}")
            return {}
        
        strategy = self.strategy_manager.create_strategy(strategy_name, **strategy_params)
        if not strategy:
            self.logger.error(f"Strategy {strategy_name} not found")
            return {}

        # Process each symbol
        for symbol, data in data_dict.items():
            if not data.empty:
                data_with_signals = self.strategy_manager.run_strategy(strategy, data)
                await self._step_through_data(data_with_signals, strategy)
        
        # Finalize backtest
        await self._finalize_backtest(data_dict)

        return self._generate_results(strategy_name, symbols, start_date, end_date)

    def _reset_state(self) -> None:
        """Reset backtest state for a new run."""
        self.order_manager = OrderManager(
            commission=self.config.get('commission', 0.001),
            slippage=self.config.get('slippage', 0.0005)
        )
        self.equity_curve = []
        # Engine owns cash; mirror into order_manager for single source accounting
        self.current_capital = float(self.initial_capital)
        self.order_manager.cash = float(self.initial_capital)

    async def _step_through_data(self, data: pd.DataFrame, strategy) -> None:
        """
        Step through data for a single symbol and execute trades.
        """
        for index, row in data.iterrows():
            timestamp = pd.Timestamp(index)  # type: ignore # Convert index to Timestamp
            await self._update_equity_curve(timestamp, {row['symbol']: row}) # type: ignore
            # Only process signals if they are valid and non-zero
            if pd.notna(row['signal']) and row['signal'] != 0:
                await self._execute_signal(row['signal'], row, timestamp) # type: ignore
            await self._check_exit_conditions(row, timestamp, strategy)

    async def _finalize_backtest(self, data_dict: Dict[str, pd.DataFrame]) -> None:
        """Close any open positions at the end of the backtest."""
        final_timestamps = {symbol: df.index[-1] for symbol, df in data_dict.items() if not df.empty}
        for position in self.order_manager.get_open_positions():
            if position.symbol in final_timestamps:
                final_price = data_dict[position.symbol].loc[final_timestamps[position.symbol], 'close']
                if isinstance(final_price, complex):
                    raise ValueError("Complex values are not supported")
                final_price = float(final_price) # type: ignore

                await self.order_manager.close_position(position.id, final_price, final_timestamps[position.symbol])

    def _generate_results(self, strategy_name, symbols, start_date, end_date) -> Dict[str, Any]:
        """
        Generate the final results dictionary.
        Ensures:
          - equity_curve is a list of {timestamp: ISO string, equity: float}
          - positions/trades are returned separately from equity_curve
          - final_capital is derived from equity_curve last value when available (fallback: initial + PnL)
        """
        from .performance import PerformanceAnalyzer
        analyzer = PerformanceAnalyzer(self.config.get('risk_free_rate', 0.02))

        # Normalize equity_curve timestamps to ISO strings and ensure floats
        normalized_equity = [
            {
                'timestamp': (ec['timestamp'].isoformat() if hasattr(ec['timestamp'], 'isoformat') else str(ec['timestamp'])),
                'equity': float(ec['equity'])
            }
            for ec in self.equity_curve
            if isinstance(ec, dict) and 'timestamp' in ec and 'equity' in ec
        ]

        # Serialize closed positions to plain dicts and provide a separate 'trades' array for UI
        closed_positions = self.order_manager.get_closed_positions()
        positions_serialized = [p.to_dict() for p in closed_positions]
        trades = []
        for p in closed_positions:
            # exit_time may be None; avoid calling isoformat on None
            exit_time_attr = getattr(p, 'exit_time', None)
            if exit_time_attr is None:
                exit_time_val = None
            else:
                exit_time_val = exit_time_attr.isoformat() if hasattr(exit_time_attr, 'isoformat') else str(exit_time_attr)

            # exit_price may be None; keep it None rather than coercing to float
            exit_price_attr = getattr(p, 'exit_price', None)
            exit_price_val = float(exit_price_attr) if exit_price_attr is not None else None

            trades.append({
                'symbol': p.symbol,
                'quantity': float(p.quantity),
                'entry_price': float(p.entry_price),
                'entry_time': (p.entry_time.isoformat() if hasattr(p.entry_time, 'isoformat') else str(p.entry_time)),
                'exit_price': exit_price_val,
                'exit_time': exit_time_val,
                'pnl': float(p.get_pnl()),
            })

        # Prefer final_capital from the last equity point if available
        if normalized_equity:
            final_capital = float(normalized_equity[-1]['equity'])
        else:
            # Fallback: initial + realized PnL
            final_capital = float(self.initial_capital + sum(p.get_pnl() for p in closed_positions))

        performance_metrics = analyzer.calculate_metrics(normalized_equity, closed_positions, self.initial_capital)

        return {
            'strategy_name': strategy_name,
            'symbol': symbols,
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': float(self.initial_capital),
            'final_capital': final_capital,
            'equity_curve': normalized_equity,
            'positions': positions_serialized,
            'trades': trades,
            'performance': performance_metrics,
        }

    async def _update_equity_curve(self, timestamp: datetime, current_data: Dict[str, pd.Series]) -> None:
        """Update the equity curve with current capital and position values."""
        total_equity = self.current_capital
        for position in self.order_manager.get_open_positions():
            if position.symbol in current_data:
                total_equity += position.quantity * current_data[position.symbol]['close']
        self.equity_curve.append({'timestamp': timestamp, 'equity': total_equity})

    async def _execute_signal(self, signal: float, row: pd.Series, timestamp: pd.Timestamp) -> None:
        """
        Execute a trading signal.
        """
        price = row['close']
        symbol = row['symbol']
        quantity = self.sizing_manager.calculate_quantity(price, self.current_capital)

        order = None
        if signal == 1:
            order = self.order_manager.create_order(symbol, quantity, OrderType.MARKET, OrderDirection.BUY)
        elif signal == -1:
            order = self.order_manager.create_order(symbol, quantity, OrderType.MARKET, OrderDirection.SELL)
        
        if order:
            position = await self.order_manager.execute_order(order, price, timestamp)
            if position and order.filled_price is not None:
                # Update current capital after a trade
                if order.direction == OrderDirection.BUY:
                    self.current_capital -= order.quantity * order.filled_price
                else:
                    self.current_capital += order.quantity * order.filled_price

    async def _check_exit_conditions(self, row: pd.Series, timestamp: pd.Timestamp, strategy) -> None:
        """
        Check for stop loss or take profit conditions.
        """
        price = row['close']
        symbol = row['symbol']
        for position in self.order_manager.get_open_positions():
            if position.symbol == symbol:
                stop_loss_pct = strategy.params.get('stop_loss_pct', 0)
                take_profit_pct = strategy.params.get('take_profit_pct', 0)

                if stop_loss_pct > 0 or take_profit_pct > 0:
                    current_return = (price - position.entry_price) / position.entry_price if position.quantity > 0 else (position.entry_price - price) / position.entry_price

                    closed_position = None
                    if stop_loss_pct > 0 and current_return <= -stop_loss_pct / 100:
                        closed_position = await self.order_manager.close_position(position.id, price, timestamp)
                        self.logger.info(f"Stop loss triggered for position {position.id}")
                    
                    elif take_profit_pct > 0 and current_return >= take_profit_pct / 100:
                        closed_position = await self.order_manager.close_position(position.id, price, timestamp)
                        self.logger.info(f"Take profit triggered for position {position.id}")

                    if closed_position and closed_position.exit_price is not None:
                        # Update capital with proceeds from the closed position
                        self.current_capital += abs(closed_position.quantity) * closed_position.exit_price - closed_position.commission
