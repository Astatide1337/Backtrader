import useSWR from 'swr';
import { ENDPOINTS } from 'lib/config';
import type { Order } from 'types/api';

export type UseOrdersResult = {
  data: Order[] | null;
  isLoading: boolean;
  error: any;
  mutate: () => void;
};

export default function useOrders(backtestId: string): UseOrdersResult {
  const { data, error, mutate, isLoading } = useSWR<Order[]>(
    backtestId ? ENDPOINTS.backtestOrders(backtestId) : null
  );
  return {
    data: data ?? null,
    isLoading: !!isLoading && !data && !error,
    error,
    mutate,
  };
}