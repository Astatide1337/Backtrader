import React from 'react';
import Card, { CardContent, CardHeader } from 'components/ui/Card';
import Button from 'components/ui/Button';
import { createOrUpdateCustomStrategy, validateCustomStrategy } from 'lib/customStrategies';
import type { StrategySchemaV1, StrategyRecord } from 'types/strategySchema';

type Props = {
  schema: StrategySchemaV1;
  setBusy?: (busy: boolean) => void;
  onSaved?: (rec: StrategyRecord) => void;
  localErrors?: string[]; // aggregated validation errors from steps
};

const StepReview: React.FC<Props> = ({ schema, setBusy, onSaved, localErrors }) => {
  const [result, setResult] = React.useState<{ ok: boolean; notes: string[] } | null>(null);
  const [errMsg, setErrMsg] = React.useState<string | null>(null);
  const [saving, setSaving] = React.useState<'draft' | 'published' | null>(null);
  const strategyIdRef = React.useRef<string | null>(null);

  async function save(status: 'draft' | 'published') {
    setErrMsg(null);
    setSaving(status);
    setBusy?.(true);
    try {
      const rec = await createOrUpdateCustomStrategy(schema, status);
      strategyIdRef.current = rec.id;
      onSaved?.(rec);
    } catch (e: any) {
      setErrMsg(e?.message || 'Failed to save.');
    } finally {
      setBusy?.(false);
      setSaving(null);
    }
  }

  async function simulate() {
    setErrMsg(null);
    setBusy?.(true);
    try {
      // If not saved yet, persist a draft temporarily to obtain id for validation
      let id = strategyIdRef.current;
      if (!id) {
        const rec = await createOrUpdateCustomStrategy(schema, 'draft');
        id = rec.id;
        strategyIdRef.current = id;
      }
      const res = await validateCustomStrategy(id!, { bars: 100 });
      setResult(res);
    } catch (e: any) {
      setErrMsg(e?.message || 'Failed to validate.');
    } finally {
      setBusy?.(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <h2 className="text-base font-semibold text-gray-900">Review & Validate</h2>
        <p className="mt-1 text-sm text-gray-600">
          Check the JSON preview, fix any local lint errors, simulate 100 bars, then save.
        </p>
      </CardHeader>
      <CardContent>
        {localErrors && localErrors.length > 0 && (
          <div role="alert" className="mb-3 rounded-md bg-red-50 p-2 text-sm text-red-700">
            <div className="font-medium">Local validation issues:</div>
            <ul className="list-inside list-disc">
              {localErrors.map((e, i) => (
                <li key={i}>{e}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <h3 className="mb-2 text-sm font-semibold text-gray-900">Summary</h3>
            <div className="rounded-md border p-3 text-sm">
              <div><span className="font-medium">Name:</span> {schema.basics.name || '—'}</div>
              <div><span className="font-medium">Indicators:</span> {schema.indicators.length}</div>
              <div><span className="font-medium">Entry groups:</span> {schema.entry.groups.length}</div>
              <div><span className="font-medium">Exit groups:</span> {schema.exit?.groups?.length ?? 0}</div>
              <div><span className="font-medium">Sizing:</span> {schema.sizing.mode}</div>
              <div><span className="font-medium">Advanced exprs:</span> {schema.advanced?.expressions?.length ?? 0}</div>
            </div>

            <div className="mt-3 space-x-2">
              <Button size="sm" onClick={simulate}>Simulate 100 bars</Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={() => save('draft')}
                loading={saving === 'draft'}
              >
                Save Draft
              </Button>
              <Button
                size="sm"
                variant="primary"
                onClick={() => save('published')}
                loading={saving === 'published'}
              >
                Publish
              </Button>
            </div>

            {errMsg && <div className="mt-2 text-sm text-red-600">{errMsg}</div>}
            {result && (
              <div className="mt-3 rounded-md border p-3 text-sm">
                <div className="font-medium">Simulation result</div>
                <div className={result.ok ? 'text-emerald-700' : 'text-amber-700'}>
                  {result.ok ? 'OK' : 'Issues detected'}
                </div>
                <ul className="mt-1 list-inside list-disc">
                  {result.notes.map((n, i) => (
                    <li key={i}>{n}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div>
            <h3 className="mb-2 text-sm font-semibold text-gray-900">JSON Preview</h3>
            <pre className="max-h-[420px] overflow-auto rounded-md border p-3 text-xs">
{JSON.stringify(schema, null, 2)}
            </pre>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default React.memo(StepReview);