import React, { useMemo, useState, useEffect } from 'react';
import { useBacktests } from 'hooks/useBacktests';
import { fetchJson } from 'lib/http';
import { ENDPOINTS } from 'lib/config';
import Card from 'components/ui/Card';
import { CardHeader, CardContent } from 'components/ui/Card';
import Input from 'components/ui/Input';
import Select from 'components/ui/Select';
import Button from 'components/ui/Button';
import ErrorState from 'components/ui/ErrorState';

type Strategy = { id: string; name: string; description?: string | null };

const NewBacktestPage: React.FC = () => {
  const { createBacktest } = useBacktests();
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loadingStrategies, setLoadingStrategies] = useState(true);
  const [errorStrategies, setErrorStrategies] = useState<string | null>(null);

  // form state
  // Preselect strategy from query string if present
  const [strategy, setStrategy] = useState<string>(() => {
    if (typeof window === 'undefined') return '';
    const sp = new URLSearchParams(window.location.search);
    return sp.get('strategy') ?? '';
  });
  const [symbol, setSymbol] = useState('AAPL');
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [capital, setCapital] = useState('100000');
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const valid = useMemo(() => {
    const cap = Number(capital);
    return strategy && symbol && start && end && !Number.isNaN(cap) && cap > 0;
  }, [strategy, symbol, start, end, capital]);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetchJson(ENDPOINTS.strategies);
        setStrategies(res.strategies ?? []);
        setErrorStrategies(null);
      } catch (e: any) {
        setErrorStrategies(e?.message || 'Failed to load strategies');
      } finally {
        setLoadingStrategies(false);
      }
    }
    load();
  }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!valid) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      // Ensure ISO date strings are passed (YYYY-MM-DD) which FastAPI/Pydantic will coerce to date
      await createBacktest({
        strategy_name: strategy,
        symbol: symbol.toUpperCase().trim(),
        start_date: start,
        end_date: end,
        initial_capital: Number(capital),
      });
      window.location.href = '/backtests';
    } catch (e: any) {
      // Surface backend validation errors (422) to the user
      const detail = e?.detail;
      const friendly =
        Array.isArray(detail)
          ? detail.map((d: any) => (d?.msg ? `${d?.loc?.join('.') ?? 'field'}: ${d.msg}` : JSON.stringify(d))).join('; ')
          : typeof detail === 'string'
            ? detail
            : e?.message || 'Failed to create backtest';
      setSubmitError(friendly);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="text-sm font-semibold text-gray-900">New Backtest</div>
        </CardHeader>
        <CardContent>
          {loadingStrategies ? (
            <div className="text-sm text-gray-600">Loading strategies…</div>
          ) : errorStrategies ? (
            <ErrorState message={errorStrategies} />
          ) : (
            <form onSubmit={onSubmit} className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-700">Strategy</label>
                <Select value={strategy} onChange={(e) => setStrategy(e.target.value)} className="select">
                  <option value="">Select a strategy</option>
                  {strategies.map((s) => (
                    <option key={s.id} value={s.name}>
                      {s.name}
                    </option>
                  ))}
                </Select>
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-gray-700">Symbol</label>
                <Input value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} />
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-gray-700">Start Date</label>
                <Input type="date" value={start} onChange={(e) => setStart(e.target.value)} />
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-gray-700">End Date</label>
                <Input type="date" value={end} onChange={(e) => setEnd(e.target.value)} />
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-gray-700">Initial Capital</label>
                <Input type="number" min="1" step="1" value={capital} onChange={(e) => setCapital(e.target.value)} />
              </div>

              <div className="sm:col-span-2 lg:col-span-3">
                <Button type="submit" disabled={!valid || submitting} className="btn btn-primary px-4 py-2">
                  {submitting ? 'Creating…' : 'Create Backtest'}
                </Button>
                {!valid && (
                  <div className="mt-2 text-xs text-gray-600">Fill all fields; capital must be a positive number.</div>
                )}
                {submitError && <div className="mt-2 text-xs text-red-600">{submitError}</div>}
              </div>
            </form>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="text-sm font-semibold text-gray-900">Delete Backtest</div>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-gray-600">
            Delete is not available: the backend does not expose a DELETE endpoint. To support deletion, add an API
            endpoint that calls the DB helper in [backend/database.py.delete_backtest_db()](backend/database.py:122-137),
            then we can wire a delete action in the list and detail pages.
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default NewBacktestPage;