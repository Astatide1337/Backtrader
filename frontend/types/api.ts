/**
 * Types modeled from backend endpoints:
 * - [backend/main.py.get("/api/v1/backtests")](backend/main.py:139-149)
 * - [backend/main.py.post("/api/v1/backtest")](backend/main.py:98-118)
 * - [backend/main.py.get("/api/v1/backtest/{backtest_id}")](backend/main.py:120-137)
 * - [backend/main.py.get("/api/v1/orders")](backend/main.py:176-187)
 * - [backend/main.py.post("/api/v1/orders")](backend/main.py:152-174)
 * - [backend/main.py.get("/api/v1/portfolio")](backend/main.py:208-220)
 * - [backend/main.py.get("/api/v1/market-data/{symbol}")](backend/main.py:222-249)
 * - [backend/main.py.get("/api/v1/strategies")](backend/main.py:251-262)
 */

// Backtests
export interface BacktestListItem {
  id: string;
  strategy_name: string;
  symbol: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  created_at: string; // ISO
}

export interface PerformanceMetrics {
  total_return: number;
  annualized_return: number;
  annualized_volatility: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  calmar_ratio: number;
  max_drawdown: number;
  win_rate: number;
  profit_factor: number;
  avg_trade: number;
  avg_win: number;
  avg_loss: number;
}

export interface Position {
  symbol: string;
  side: 'long' | 'short';
  quantity: number;
  entry_price: number;
  exit_price: number | null;
  pnl: number;
  entry_time: string;
  exit_time: string | null;
}

export interface BacktestDetail {
  id: string;
  strategy_name: string;
  symbol: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital: number;
  equity_curve: { timestamp: string; equity: number }[];
  price_curve?: { timestamp: string; price: number }[];
  positions: Position[];
  performance: PerformanceMetrics;
  orders: Order[];
}

// Orders
export interface Order {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  qty: number;
  price: number;
  timestamp: string; // ISO
  status?: 'filled' | 'pending' | 'cancelled' | 'rejected';
}

// Portfolio
export interface PortfolioSnapshot {
  timestamp: string; // ISO
  equity: number;
  cash: number;
  pnl: number;
}

// Strategies
export interface Strategy {
  id: string;
  name: string;
  description?: string | null;
}

// Market data
export interface MarketCandle {
  timestamp: string; // ISO
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}
