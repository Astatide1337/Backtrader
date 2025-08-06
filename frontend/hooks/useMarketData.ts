import useSWR from 'swr';
import { ENDPOINTS } from 'lib/config';
import type { MarketCandle } from 'types/api';

export type UseMarketDataResult = {
  data: MarketCandle[] | null;
  isLoading: boolean;
  error: any;
  mutate: () => void;
};

export default function useMarketData(symbol: string, limit = 100): UseMarketDataResult {
  const key = symbol ? `${ENDPOINTS.marketDataBySymbol(symbol)}?limit=${limit}` : null;
  const { data, error, mutate, isLoading } = useSWR<MarketCandle[]>(key);
  return {
    data: data ?? null,
    isLoading: !!isLoading && !data && !error,
    error,
    mutate,
  };
}