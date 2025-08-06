import type { SWRConfiguration } from 'swr';
import { fetchJson } from 'lib/http';

export const swrConfig: SWRConfiguration = {
  fetcher: (key: string) => fetchJson(key),
  revalidateOnFocus: true,
  errorRetryCount: 2,
  dedupingInterval: 1000,
  shouldRetryOnError: true,
};