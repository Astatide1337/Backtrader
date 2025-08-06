import useSWR from 'swr';
import { ENDPOINTS } from 'lib/config';
import type { PortfolioSnapshot } from 'types/api';

export type UsePortfolioResult = {
  data: PortfolioSnapshot | null;
  isLoading: boolean;
  error: any;
  mutate: () => void;
};

export default function usePortfolio(): UsePortfolioResult {
  const { data, error, mutate, isLoading } = useSWR<PortfolioSnapshot>(ENDPOINTS.portfolio);
  return {
    data: data ?? null,
    isLoading: !!isLoading && !data && !error,
    error,
    mutate,
  };
}