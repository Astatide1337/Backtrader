import { fetchJson } from 'lib/http';
import type { StrategySchemaV1, StrategyRecord } from 'types/strategySchema';

export async function createOrUpdateCustomStrategy(
  schema: StrategySchemaV1,
  status: 'draft' | 'published',
): Promise<StrategyRecord> {
  const payload = await fetchJson<StrategyRecord>('/api/v1/strategies/custom', {
    method: 'POST',
    body: { status, strategy: schema },
  });
  return payload;
}

export async function listCustomStrategies(): Promise<StrategyRecord[]> {
  const payload = await fetchJson<{ strategies: StrategyRecord[] } | StrategyRecord[]>(
    '/api/v1/strategies/custom',
  );
  if (Array.isArray(payload)) return payload;
  if (payload && 'strategies' in payload) return payload.strategies;
  return [];
}

export async function getCustomStrategy(id: string): Promise<StrategyRecord> {
  const payload = await fetchJson<StrategyRecord>(`/api/v1/strategies/custom/${encodeURIComponent(id)}`);
  return payload;
}

export async function validateCustomStrategy(
  id: string,
  options: { bars?: number } = { bars: 100 },
): Promise<{ ok: boolean; notes: string[] }> {
  const payload = await fetchJson<{ ok: boolean; notes: string[] }>(
    `/api/v1/strategies/custom/${encodeURIComponent(id)}/validate`,
    { method: 'POST', body: { options } },
  );
  return payload;
}

export async function deleteCustomStrategy(id: string): Promise<void> {
  await fetchJson<void>(`/api/v1/strategies/custom/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  });
}
