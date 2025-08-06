
import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging

from .config import Config
from .data_manager import DataManager
from .strategy_manager import StrategyManager
from .order_manager import OrderManager, OrderType, OrderDirection

class AsyncBacktestEngine:
    """Asynchronous backtesting engine with cash-aware accounting."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the asynchronous backtesting engine.
        
        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.data_manager = DataManager(cache_dir=self.config.get('cache_dir', './data/cache'))
        self.strategy_manager = StrategyManager()
        self.order_manager = OrderManager(
            commission=self.config.get('commission', 0.001),
            slippage=self.config.get('slippage', 0.0005)
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        self.initial_capital = float(self.config.get('initial_capital', 10000))
        self.equity_curve: List[Dict[str, Any]] = []
        # Initialize broker-like cash in OrderManager
        if not hasattr(self.order_manager, "cash"):
            self.order_manager.cash = 0.0
        self.order_manager.cash = float(self.initial_capital)
        self.logger.debug(f"[INIT] initial_capital={self.initial_capital} cash={self.order_manager.cash}")
        # Instrumentation
        self.logger.setLevel(logging.DEBUG)
        
    async def run_backtest(self, strategy_name: str, symbols: Union[str, List[str]], start_date: Union[str, datetime], 
                             end_date: Union[str, datetime], **strategy_params) -> Dict[str, Any]:
        """
        Run a backtest asynchronously on one or more symbols.
        """
        self._reset_state()
        
        data_dict = self.data_manager.fetch_data(symbols, start_date, end_date)
        if not data_dict:
            self.logger.error(f"No data found for symbols: {symbols}")
            return {}
        
        strategy = self.strategy_manager.create_strategy(strategy_name, **strategy_params)
        if not strategy:
            self.logger.error(f"Strategy {strategy_name} not found")
            return {}
        
        # Normalize each symbol DataFrame: ensure a 'symbol' column and a DatetimeIndex named 'date'
        normalized = []
        signals_dict = {}
        for symbol, df in data_dict.items():
            df = df.copy()
            df['symbol'] = symbol
            # Ensure datetime index
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
            df.index.name = 'date'
            normalized.append(df)
            # Precompute signals per symbol (aligned to df index)
            sig = self.strategy_manager.run_strategy(strategy, df)['signal']
            signals_dict[symbol] = sig

        # Combine into MultiIndex: (symbol, date)
        combined_data = pd.concat(normalized)
        combined_data = combined_data.set_index(['symbol'], append=True).reorder_levels(['symbol', 'date'])
        combined_data.sort_index(inplace=True)

        await self._step_through_data(combined_data, signals_dict, strategy)
        
        final_capital = float(self.equity_curve[-1]['equity']) if self.equity_curve else float(self.initial_capital)

        from .performance import PerformanceAnalyzer
        analyzer = PerformanceAnalyzer(self.config.get('risk_free_rate', 0.02))
        # Analyzer must use the same equity_curve we appended (cash + MTM) and the same closed positions list
        performance_metrics = analyzer.calculate_metrics(self.equity_curve, self.order_manager.get_closed_positions(), self.initial_capital)

        return {
            'strategy_name': strategy_name,
            'symbol': symbols,
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': self.initial_capital,
            'final_capital': final_capital,
            'equity_curve': self.equity_curve,
            'positions': [
                {
                    "symbol": p.symbol,
                    "quantity": p.quantity,
                    "entry_price": p.entry_price,
                    "entry_time": p.entry_time,
                    "exit_price": p.exit_price,
                    "exit_time": p.exit_time,
                    "pnl": p.get_pnl(),
                    # Add explicit side and notionals for transparency (long/short clarity)
                    "side": "long" if p.quantity > 0 else "short",
                    "entry_notional": (abs(p.quantity) * p.entry_price) if (p.entry_price is not None) else None,
                    "exit_notional": (abs(p.quantity) * p.exit_price) if (p.exit_price is not None) else None,
                }
                for p in self.order_manager.get_closed_positions()
            ],
            'performance': performance_metrics,
        }
    
    def _reset_state(self) -> None:
        """Reset backtest state."""
        self.order_manager = OrderManager(
            commission=self.config.get('commission', 0.001),
            slippage=self.config.get('slippage', 0.0005)
        )
        # Reset instrumentation targets
        self.equity_curve = []
        # Align with broker-like model: cash tracked in OrderManager
        if not hasattr(self.order_manager, "cash"):
            self.order_manager.cash = 0.0
        self.order_manager.cash = float(self.initial_capital)
        self.logger.debug(f"[RESET] initial_capital={self.initial_capital} cash={self.order_manager.cash}")
    
    async def _step_through_data(self, data: pd.DataFrame, signals: Dict[str, pd.Series], strategy) -> None:
        """
        Step through multi-asset data and execute trades.
        """
        # Cash is kept in self.order_manager.cash. Keep a local alias for logging.
        for timestamp, group in data.groupby(level=1):
            # Compute equity = cash + MTM of open positions
            cash = float(self.order_manager.cash)
            current_equity = cash
            syms = set(group.index.get_level_values('symbol'))
            for pos in self.order_manager.get_open_positions():
                if pos.symbol in syms:
                    price = float(group.loc[(pos.symbol, timestamp), 'close'])
                    current_equity += float(pos.quantity) * price
            self.equity_curve.append({'timestamp': timestamp, 'equity': float(current_equity)})
            self.logger.debug(f"[EQ] t={timestamp} cash={cash:.2f} equity={current_equity:.2f} open_pos={len(self.order_manager.get_open_positions())}")

            for idx, row in group.iterrows():
                symbol = idx[0]
                signal = signals[symbol].get(timestamp)
                if signal is not None and signal != 0:
                    pre_cash = self.order_manager.cash
                    await self._execute_signal(signal, row, timestamp)
                    post_cash = self.order_manager.cash
                    self.logger.debug(f"[EXEC] {symbol} signal={signal} cash:{pre_cash:.2f}->{post_cash:.2f}")

                await self._check_exit_conditions(row['close'], timestamp, strategy, symbol)
            
            await asyncio.sleep(0)

    async def _execute_signal(self, signal: float, row: pd.Series, timestamp: pd.Timestamp) -> None:
        """
        Execute a trading signal for a specific symbol.
        Sizing uses available cash (no leverage). Cash is mutated inside OrderManager on fill.
        """
        price = float(row['close'])
        symbol = str(row.name[0])
        available_cash = float(self.order_manager.cash)
        if price <= 0:
            self.logger.debug(f"[SIZE] Skip non-positive price at {timestamp}")
            return
        # Simple percentage sizing based on config (default 10%)
        pct = float(self.config.get('sizing_percentage', 0.1))
        notional = available_cash * pct
        quantity = int(notional // price)
        if quantity <= 0:
            self.logger.debug(f"[SIZE] Zero qty at {timestamp} price={price} cash={available_cash} pct={pct}")
            return

        if signal == 1:
            order = self.order_manager.create_order(symbol, quantity, OrderType.MARKET, OrderDirection.BUY)
            await self.order_manager.execute_order(order, price, timestamp)
        elif signal == -1:
            # Close full if we have an open position; otherwise skip
            order = self.order_manager.create_order(symbol, quantity, OrderType.MARKET, OrderDirection.SELL)
            await self.order_manager.execute_order(order, price, timestamp)
        # Cash updates are handled by OrderManager.execute_order
        return None

    async def _check_exit_conditions(self, price: float, timestamp: pd.Timestamp, strategy, symbol: str) -> None:
        """
        Check for stop loss or take profit conditions for a specific symbol.
        """
        for position in list(self.order_manager.get_open_positions()):
            if position.symbol == symbol:
                stop_loss_pct = strategy.params.get('stop_loss_pct', 0)
                take_profit_pct = strategy.params.get('take_profit_pct', 0)

                if stop_loss_pct > 0 or take_profit_pct > 0:
                    current_return = (price - position.entry_price) / position.entry_price if position.quantity > 0 else (position.entry_price - price) / position.entry_price

                    if stop_loss_pct > 0 and current_return <= -stop_loss_pct / 100:
                        pre = self.order_manager.cash
                        await self.order_manager.close_position(position.id, price, timestamp)
                        post = self.order_manager.cash
                        self.logger.debug(f"[SL] Closed {position.id} ret={current_return:.4f} cash:{pre:.2f}->{post:.2f}")
                    
                    elif take_profit_pct > 0 and current_return >= take_profit_pct / 100:
                        pre = self.order_manager.cash
                        await self.order_manager.close_position(position.id, price, timestamp)
                        post = self.order_manager.cash
                        self.logger.debug(f"[TP] Closed {position.id} ret={current_return:.4f} cash:{pre:.2f}->{post:.2f}")
