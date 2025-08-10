import { fetchJson, HttpError } from 'lib/http';
import { API_BASE_URL } from 'lib/config';
import Toast from 'components/ui/Toast';
import { v4 as uuidv4 } from 'uuid';
import type {
  StrategySchemaV1,
  StrategyRecord,
  StrategyStore,
} from 'types/strategySchema';

// Simple toast bus for showing fallback notices without wiring global provider
// We'll render a one-off Toast for a few seconds.
let toastContainer: HTMLDivElement | null = null;
function showToast(message: string, variant: 'info' | 'success' | 'error' | 'warning' = 'warning') {
  if (typeof window === 'undefined') return;
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    document.body.appendChild(toastContainer);
  }
  const root = toastContainer;
  const close = () => {
    if (!root) return;
    root.innerHTML = '';
  };
  // Render a simple inline React component using Toast
  // Note: This avoids creating a global context; adequate for this stub.
  const React = require('react');
  const ReactDOM = require('react-dom');
  ReactDOM.render(
    React.createElement(Toast, {
      open: true,
      title: 'Using local mock',
      description: message,
      variant,
      onClose: close,
      duration: 2500,
    }),
    root,
  );
}

const LS_KEY = 'bt_custom_strategies';

function readStore(): StrategyStore {
  if (typeof window === 'undefined') return { strategies: [] };
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (!raw) return { strategies: [] };
    const parsed = JSON.parse(raw) as StrategyStore;
    if (!parsed || !Array.isArray(parsed.strategies)) return { strategies: [] };
    return parsed;
  } catch {
    return { strategies: [] };
  }
}

function writeStore(store: StrategyStore) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(LS_KEY, JSON.stringify(store));
}

function upsertLocal(schema: StrategySchemaV1, status: 'draft' | 'published'): StrategyRecord {
  const store = readStore();
  // naive: if schema has basics.name matching an existing record, update; else create a new id
  // Prefer using id if advanced stored but in our flow create path doesn't have id until after return.
  let rec = store.strategies.find((s) => s.strategy.basics.name.trim() === schema.basics.name.trim());
  const now = new Date().toISOString();
  if (rec) {
    rec.status = status;
    rec.strategy = schema;
    rec.updated_at = now;
  } else {
    rec = {
      id: uuidv4(),
      status,
      created_at: now,
      updated_at: now,
      strategy: schema,
    };
    store.strategies.unshift(rec);
  }
  writeStore(store);
  return rec;
}

function listLocal(): StrategyRecord[] {
  return readStore().strategies;
}

function getLocal(id: string): StrategyRecord | null {
  return readStore().strategies.find((s) => s.id === id) ?? null;
}

function validateLocal(id: string, _options: any): { ok: boolean; notes: string[] } {
  // Minimal mock validation: ensure basics name exists and at least one entry group present
  const rec = getLocal(id);
  const notes: string[] = [];
  if (!rec) return { ok: false, notes: ['Not found in local mock'] };
  if (!rec.strategy.basics.name) notes.push('Name missing');
  const hasEntry = rec.strategy.entry?.groups?.some((g) => (g.conditions?.length ?? 0) > 0);
  if (!hasEntry) notes.push('No entry conditions present');
  return { ok: notes.length === 0, notes: notes.length ? notes : ['Validation passed (mock)'] };
}

// Attempt real backend first; on 404/501/NetworkError fallback to local mock and show toast.
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
  if (payload && 'strategies' in (payload as any)) return (payload as any).strategies;
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
