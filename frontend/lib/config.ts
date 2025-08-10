export const API_BASE_URL: string =
  (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_BASE_URL) || 'http://localhost:8000';

export const ENDPOINTS = {
  backtests: '/api/v1/backtests',
  backtestById: (id: string | number) => `/api/v1/backtest/${id}`,
  backtestCreate: '/api/v1/backtest',
  backtestDelete: (id: string | number) => `/api/v1/backtest/${id}`,
  backtestOrders: (id: string | number) => `/api/v1/backtests/${id}/orders`,
  orders: '/api/v1/orders',
  portfolio: '/api/v1/portfolio',
  strategies: '/api/v1/strategies',
  marketDataBySymbol: (symbol: string) => `/api/v1/market-data/${symbol}`,
} as const;