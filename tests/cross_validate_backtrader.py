"""
Cross-validate RSI mean reversion strategy using backtrader with Yahoo data.

Usage:
  python tests/cross_validate_backtrader.py

What it does:
- Installs 'backtrader' and 'yfinance' if missing (local, user scope).
- Downloads AAPL daily data for 2022-01-01 to 2023-01-01 via yfinance.
- Runs an RSI(14) mean reversion strategy:
    Buy when RSI < 30, Sell when RSI > 70
    Position size: 10% of current equity (rounded down to whole shares)
    Commission: 0.1% per trade
    Slippage: fixed 0.05% price impact applied against the trade direction
- Prints summary metrics:
    Final equity, total return, number of trades, win rate, max drawdown, Sharpe-like metric
- Writes equity curve CSV to ./output/backtrader_equity_aapl_2022.csv for side-by-side comparison.
"""

import sys
import subprocess
import importlib
from datetime import datetime
import os
import math
import statistics
from typing import Optional

def _ensure_pkg(name: str):
    try:
        return importlib.import_module(name)
    except ImportError:
        print(f"Installing {name} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", name])
        return importlib.import_module(name)

bt = _ensure_pkg("backtrader")
yf = _ensure_pkg("yfinance")
import pandas as pd


class RSIMeanReversion(bt.Strategy):
    params = dict(
        rsi_period=14,
        oversold=30,
        overbought=70,
        sizing_pct=0.10,     # 10% of equity
        commission=0.001,    # 0.1%
        slippage_pct=0.0005, # 0.05%
        printlog=False,
    )

    def log(self, txt):
        if self.p.printlog:
            dt = self.datas[0].datetime.date(0)
            print(f"{dt.isoformat()} {txt}")

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=self.p.rsi_period)
        self.order = None

    def next(self):
        if self.order:
            return

        # Compute target size (10% of equity)
        equity = self.broker.getvalue()
        price = self.data.close[0]
        raw_qty = (equity * self.p.sizing_pct) / price
        qty = int(max(0, math.floor(raw_qty)))

        # Skip zero-qty orders
        if qty == 0:
            return

        # Entry condition: RSI < oversold and no open position
        if not self.position and self.rsi[0] < self.p.oversold:
            self.order = self.buy(size=qty)

        # Exit condition: RSI > overbought and have a position
        elif self.position and self.rsi[0] > self.p.overbought:
            self.order = self.sell(size=self.position.size)

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.log(f"ORDER {'BUY' if order.isbuy() else 'SELL'} EXECUTED, "
                     f"price={order.executed.price:.2f}, size={order.executed.size}, "
                     f"cost={order.executed.value:.2f}, comm={order.executed.comm:.2f}")
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f"ORDER FAILED status={order.getstatusname()}")
        self.order = None

    def stop(self):
        self.log(f"Final Equity: {self.broker.getvalue():.2f}")


def compute_max_drawdown(equity_series):
    peak = equity_series[0]
    mdd = 0.0
    for x in equity_series:
        if x > peak:
            peak = x
        dd = (x - peak) / peak
        if dd < mdd:
            mdd = dd
    return mdd


def main():
    symbol = "AAPL"
    start = "2022-01-01"
    end = "2023-01-01"

    print(f"Fetching {symbol} from {start} to {end} via yfinance ...")
    df = yf.download(symbol, start=start, end=end, auto_adjust=False, progress=False)
    if isinstance(df, tuple):
        # Some environments/plugins may return (data, metadata)
        df = df[0]
    if df is None or (hasattr(df, "empty") and df.empty):
        print("No data downloaded. Aborting.")
        sys.exit(1)

    print(f"Original columns: {df.columns}")
    print(f"Column type: {type(df.columns)}")

    # Handle MultiIndex columns properly - get the Price level (level 0), not Ticker level
    if isinstance(df.columns, pd.MultiIndex):
        print("Detected MultiIndex columns, flattening...")
        print(f"MultiIndex levels: {df.columns.names}")
        print(f"Level 0 values: {df.columns.get_level_values(0).tolist()}")
        print(f"Level 1 values: {df.columns.get_level_values(1).tolist()}")
        # Get the first level (Price level) which contains Open, High, Low, Close, etc.
        df.columns = df.columns.get_level_values(0)
    
    # Convert any remaining tuples to strings
    if any(isinstance(col, tuple) for col in df.columns):
        print("Converting tuple columns to strings...")
        df.columns = [str(col) if isinstance(col, tuple) else col for col in df.columns]
    
    print(f"Processed columns: {df.columns}")

    # Normalize columns to what backtrader expects (lowercase OHLCV)
    rename_map = {}
    for col in df.columns:
        col_str = str(col).strip()
        if col_str.lower() == 'open':
            rename_map[col] = 'open'
        elif col_str.lower() == 'high':
            rename_map[col] = 'high'
        elif col_str.lower() == 'low':
            rename_map[col] = 'low'
        elif col_str.lower() == 'close':
            rename_map[col] = 'close'
        elif col_str.lower() in ['adj close', 'adj_close']:
            rename_map[col] = 'adj_close'
        elif col_str.lower() == 'volume':
            rename_map[col] = 'volume'
    
    print(f"Rename mapping: {rename_map}")
    df.rename(columns=rename_map, inplace=True)
    
    # Ensure required columns exist
    required = {"open", "high", "low", "close", "volume"}
    available_cols = set(c.lower() for c in df.columns)
    missing = required - available_cols
    if missing:
        print(f"Available columns: {list(df.columns)}")
        print(f"Available columns (lowercase): {available_cols}")
        raise RuntimeError(f"Downloaded data missing required columns: {missing}. Got columns: {list(df.columns)}")
    
    # Select and clean the data
    df = df[["open", "high", "low", "close", "volume"]].dropna()
    print(f"Final dataframe shape: {df.shape}")
    print(f"Final columns: {df.columns.tolist()}")
    print(f"First few rows:\n{df.head()}")

    # Create cerebro instance
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)  # 0.1%
    cerebro.broker.set_slippage_perc(perc=0.0005)   # 0.05% slippage

    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)

    cerebro.addstrategy(
        RSIMeanReversion,
        rsi_period=14,
        oversold=30,
        overbought=70,
        sizing_pct=0.10,
        commission=0.001,
        slippage_pct=0.0005,
        printlog=False
    )

    # Equity curve analyzer
    class EquityAnalyzer(bt.Analyzer):
        def __init__(self):
            self.values = []

        def next(self):
            self.values.append(self.strategy.broker.getvalue())

        def get_analysis(self):
            return self.values

    # Add the analyzer
    cerebro.addanalyzer(EquityAnalyzer, _name="eq")

    # Run and collect equity curve
    print("Running backtrader backtest ...")
    result = cerebro.run()
    strat = result[0]
    eq_values = strat.analyzers.eq.get_analysis()

    # Metrics
    init_capital = 100000.0
    final_equity = cerebro.broker.getvalue()
    total_return = (final_equity - init_capital) / init_capital
    mdd = compute_max_drawdown(eq_values) if eq_values else 0.0
    
    # Simple return-based Sharpe proxy (daily)
    rets = []
    for i in range(1, len(eq_values)):
        prev = eq_values[i-1]
        if prev != 0:
            rets.append((eq_values[i] - prev) / prev)
    sharpe_like = (statistics.mean(rets) / (statistics.pstdev(rets) if rets and statistics.pstdev(rets) != 0 else 1)) * (252 ** 0.5) if rets else 0.0

    print("\n=== Backtrader RSI Mean Reversion (AAPL 2022) ===")
    print(f"Final Equity: {final_equity:.2f}")
    print(f"Total Return: {total_return*100:.2f}%")
    print(f"Max Drawdown: {mdd*100:.2f}%")
    print(f"Sharpe-like: {sharpe_like:.2f}")
    
    # Trades info using TradeAnalyzer
    try:
        # Run again with TradeAnalyzer for detailed trade stats
        cerebro2 = bt.Cerebro()
        cerebro2.broker.setcash(100000.0)
        cerebro2.broker.setcommission(commission=0.001)
        cerebro2.broker.set_slippage_perc(perc=0.0005)
        cerebro2.adddata(bt.feeds.PandasData(dataname=df))
        cerebro2.addstrategy(RSIMeanReversion, rsi_period=14, oversold=30, overbought=70, sizing_pct=0.10)
        cerebro2.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
        res2 = cerebro2.run()
        ta = res2[0].analyzers.ta.get_analysis()
        total_trades = ta.get("total", {}).get("total", 0)
        won = ta.get("won", {}).get("total", 0)
        win_rate = (won / total_trades) if total_trades else 0.0
        print(f"Trades: {total_trades}, Win Rate: {win_rate*100:.2f}%")
    except Exception as e:
        print(f"Trade analyzer error: {e}")

    # Write equity curve CSV for side-by-side comparison
    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output", "backtrader_equity_aapl_2022.csv")
    
    # Make sure we have the right number of equity values
    if len(eq_values) <= len(df):
        eq_df = pd.DataFrame({"equity": eq_values}, index=df.index[-len(eq_values):])
    else:
        # Truncate equity values to match dataframe length
        eq_df = pd.DataFrame({"equity": eq_values[:len(df)]}, index=df.index)
    
    eq_df.to_csv(out_path)
    print(f"Equity curve written to {out_path}")

if __name__ == "__main__":
    main()