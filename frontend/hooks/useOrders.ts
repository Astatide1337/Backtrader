import useSWR from 'swr';
import { ENDPOINTS } from 'lib/config';
import type { Order } from 'types/api';

export type UseOrdersResult = {
  data: Order[] | null;
  isLoading: boolean;
  error: any;
  mutate: () => void;
};

export default function useOrders(): UseOrdersResult {
  const { data, error, mutate, isLoading } = useSWR<Order[]>(ENDPOINTS.orders);
  return {
    data: data ?? null,
    isLoading: !!isLoading && !data && !error,
    error,
    mutate,
  };
}