import useSWR from 'swr';
import { ENDPOINTS } from 'lib/config';
import type { Strategy } from 'types/api';

type StrategiesResponse = { strategies: Strategy[] } | Strategy[] | null | undefined;

export type UseStrategiesResult = {
  data: Strategy[] | null;
  isLoading: boolean;
  error: any;
  mutate: () => void;
};

export default function useStrategies(): UseStrategiesResult {
  const { data, error, mutate, isLoading } = useSWR<StrategiesResponse>(ENDPOINTS.strategies);
  // Unwrap payloads of either shape: { strategies: [...] } or direct array
  const list = Array.isArray(data) ? data : (data && 'strategies' in (data as any) ? (data as any).strategies : null);

  return {
    data: list ?? null,
    isLoading: !!isLoading && !list && !error,
    error,
    mutate,
  };
}