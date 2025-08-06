import useSWR from 'swr';
import { listCustomStrategies, getCustomStrategy } from 'lib/customStrategies';
import type { StrategyRecord } from 'types/strategySchema';

// We can't rely on global SWR fetcher for our stub since we sometimes use localStorage fallback.
// So we provide key-based fetchers.

export function useCustomStrategiesList() {
  const { data, error, mutate, isLoading } = useSWR<StrategyRecord[]>(
    '/api/v1/strategies/custom',
    () => listCustomStrategies(),
    { shouldRetryOnError: true, dedupingInterval: 1000 },
  );

  return {
    data: data ?? null,
    error,
    isLoading: !!isLoading && !data && !error,
    mutate,
  };
}

export function useCustomStrategy(id: string | undefined) {
  const shouldFetch = !!id;
  const { data, error, mutate, isLoading } = useSWR<StrategyRecord>(
    shouldFetch ? `/api/v1/strategies/custom/${id}` : null,
    () => getCustomStrategy(id as string),
    { shouldRetryOnError: true, dedupingInterval: 1000 },
  );

  return {
    data: data ?? null,
    error,
    isLoading: !!isLoading && !data && !error,
    mutate,
  };
}