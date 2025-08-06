import { API_BASE_URL } from 'lib/config';

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

type FetchJsonOptions = {
  method?: HttpMethod;
  headers?: Record<string, string>;
  body?: unknown;
  signal?: AbortSignal;
  retries?: number; // number of retry attempts on network errors or 5xx
  retryDelayMs?: number; // base delay
};

export class HttpError extends Error {
  status: number;
  payload: unknown;
  constructor(message: string, status: number, payload: unknown) {
    super(message);
    this.name = 'HttpError';
    this.status = status;
    this.payload = payload;
  }
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export async function fetchJson<T = unknown>(
  path: string,
  { method = 'GET', headers, body, signal, retries = 2, retryDelayMs = 400 }: FetchJsonOptions = {},
): Promise<T> {
  const url = path.startsWith('http') ? path : `${API_BASE_URL}${path}`;
  const finalHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(headers || {}),
  };

  let attempt = 0;
  // simple retry on network error or 5xx
  // do not retry on 4xx
  // exponential backoff
  // eslint-disable-next-line no-constant-condition
  while (true) {
    try {
      const res = await fetch(url, {
        method,
        headers: finalHeaders,
        body: body !== undefined ? JSON.stringify(body) : undefined,
        signal,
      });

      const isJson = res.headers.get('content-type')?.includes('application/json');
      const data = isJson ? await res.json().catch(() => null) : await res.text().catch(() => null);

      if (!res.ok) {
        if (res.status >= 500 && attempt < retries) {
          attempt += 1;
          await sleep(retryDelayMs * attempt);
          continue;
        }
        throw new HttpError(
          `Request failed with status ${res.status}`,
          res.status,
          data ?? null,
        );
      }

      return (data as T) ?? (undefined as unknown as T);
    } catch (err: any) {
      if (err?.name === 'AbortError') throw err;
      if (attempt < retries) {
        attempt += 1;
        await sleep(retryDelayMs * attempt);
        continue;
      }
      throw err;
    }
  }
}