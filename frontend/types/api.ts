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
  name: string;
  created_at: string; // ISO
  status: 'pending' | 'running' | 'completed' | 'failed';
}

export interface BacktestDetail {
  id: string;
  name: string;
  created_at: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  metrics?: Record<string, number | string | null>;
  notes?: string | null;
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