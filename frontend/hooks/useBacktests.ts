import useSWR from 'swr';
import { ENDPOINTS } from 'lib/config';
import { fetchJson } from 'lib/http';
import type { BacktestListItem, BacktestDetail } from 'types/api';

export type UseBacktestsResult = {
  data: BacktestListItem[] | null;
  isLoading: boolean;
  error: any;
  mutate: () => void;
  createBacktest: (payload: {
    strategy_name: string;
    symbol: string;
    start_date: string;
    end_date: string;
    initial_capital: number;
    parameters?: Record<string, any>;
  }) => Promise<BacktestDetail>;
  deleteBacktest: (id: string) => Promise<void>;
};

type BacktestsResponse = { backtests: BacktestListItem[] };

export function useBacktests(): UseBacktestsResult {
  const { data, error, mutate, isLoading } = useSWR<BacktestsResponse>(ENDPOINTS.backtests);
  const list = data?.backtests ?? null;

  async function createBacktest(payload: {
    strategy_name: string;
    symbol: string;
    start_date: string;
    end_date: string;
    initial_capital: number;
    parameters?: Record<string, any>;
  }) {
    // FastAPI/Pydantic is rejecting when the body is a raw JSON string (double-encoded).
    // Our fetchJson already stringifies body when provided under 'body' option.
    // So here we must pass the object under 'body' WITHOUT JSON.stringify.
    const res = await fetchJson(ENDPOINTS.backtestCreate, {
      method: 'POST',
      body: {
        strategy_name: payload.strategy_name,
        symbol: payload.symbol,
        start_date: payload.start_date,
        end_date: payload.end_date,
        initial_capital: payload.initial_capital,
        parameters: payload.parameters ?? {},
      },
      headers: { 'Content-Type': 'application/json' },
    });
    await mutate(); // refresh list
    return res as BacktestDetail;
  }

  async function deleteBacktest(id: string) {
    await fetchJson(ENDPOINTS.backtestDelete(id), { method: 'DELETE' });
    await mutate();
  }

  return {
    data: list,
    isLoading: !!isLoading && !list && !error,
    error,
    mutate,
    createBacktest,
    deleteBacktest,
  };
}

export function useBacktestDetail(id?: string | number) {
  const key = id ? ENDPOINTS.backtestById(String(id)) : null;
  const { data, error, mutate, isLoading } = useSWR<BacktestDetail>(key);
  return {
    data: data ?? null,
    isLoading: !!isLoading && !data && !error,
    error,
    mutate,
  };
}

/**
 * Utility: format ISO timestamp in user's local timezone
 */
export function formatLocalDateTime(iso?: string | number | Date) {
  if (!iso) return '—';
  // Normalize various ISO-like inputs and ensure it's interpreted in local TZ.
  // If the backend sends 'YYYY-MM-DD HH:MM:SS' or lacks timezone, Date will treat it as local.
  // If it sends '...Z' (UTC), Intl.DateTimeFormat without timeZone converts to local by default.
  const d = new Date(iso);
  if (isNaN(d.getTime())) return '—';
  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
  }).format(d);
}