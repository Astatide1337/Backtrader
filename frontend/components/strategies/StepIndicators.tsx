import React from 'react';
import Card, { CardContent, CardHeader } from 'components/ui/Card';
import Input from 'components/ui/Input';
import Select from 'components/ui/Select';
import Button from 'components/ui/Button';
import { validateIndicatorsUniqueIds } from 'types/strategySchema';
import type { IndicatorSpec, StrategySchemaV1, Timeframe } from 'types/strategySchema';

type Props = {
  value: StrategySchemaV1['indicators'];
  onChange: (v: StrategySchemaV1['indicators']) => void;
};

const indicatorTypes = [
  { value: 'sma', label: 'SMA' },
  { value: 'ema', label: 'EMA' },
  { value: 'rsi', label: 'RSI' },
  { value: 'macd', label: 'MACD' },
];

const timeframes: { value: Timeframe; label: string }[] = [
  { value: '1m', label: '1m' },
  { value: '5m', label: '5m' },
  { value: '15m', label: '15m' },
  { value: '1h', label: '1h' },
  { value: '4h', label: '4h' },
  { value: '1d', label: '1d' },
];

function newIndicator(): IndicatorSpec {
  return {
    id: '',
    type: 'sma',
    params: [{ key: 'period', value: 14 }],
    source: { type: 'price', field: 'close' },
    timeframe: '1d',
  };
}

const StepIndicators: React.FC<Props> = ({ value, onChange }) => {
  const [items, setItems] = React.useState<IndicatorSpec[]>(value);
  const [errors, setErrors] = React.useState<string[]>([]);

  React.useEffect(() => {
    setItems(value);
  }, [value]);

  function commit(next: IndicatorSpec[]) {
    setItems(next);
    onChange(next);
    setErrors(validateIndicatorsUniqueIds(next));
  }

  function update(idx: number, patch: Partial<IndicatorSpec>) {
    const next = items.map((it, i) => (i === idx ? { ...it, ...patch } : it));
    commit(next);
  }

  function add() {
    commit([...(items || []), newIndicator()]);
  }

  function remove(idx: number) {
    commit(items.filter((_, i) => i !== idx));
  }

  function updateParam(idx: number, pIdx: number, patch: Partial<NonNullable<IndicatorSpec['params']>[number]>) {
    const next = items.map((it, i) => {
      if (i !== idx) return it;
      const params = [...(it.params || [])];
      params[pIdx] = { ...params[pIdx], ...patch };
      return { ...it, params };
    });
    commit(next);
  }

  function addParam(idx: number) {
    const next = items.map((it, i) => {
      if (i !== idx) return it;
      const params = [...(it.params || []), { key: '', value: 0 }];
      return { ...it, params };
    });
    commit(next);
  }

  function removeParam(idx: number, pIdx: number) {
    const next = items.map((it, i) => {
      if (i !== idx) return it;
      const params = (it.params || []).filter((_, j) => j !== pIdx);
      return { ...it, params };
    });
    commit(next);
  }

  return (
    <Card>
      <CardHeader>
        <h2 className="text-base font-semibold text-gray-900">Indicators</h2>
        <p className="mt-1 text-sm text-gray-600">Add indicators with types, parameters, source, and timeframe.</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {items.length === 0 && <p className="text-sm text-gray-600">No indicators yet.</p>}
          {items.map((ind, idx) => (
            <div key={idx} className="rounded-md border p-3">
              <div className="grid grid-cols-1 gap-3 md:grid-cols-5">
                <Input
                  label="ID"
                  value={ind.id}
                  onChange={(e) => update(idx, { id: e.target.value })}
                  placeholder="unique id (e.g., rsi14)"
                />
                <Select
                  label="Type"
                  value={ind.type}
                  onChange={(e) => update(idx, { type: e.target.value })}
                  options={indicatorTypes}
                />
                <Select
                  label="Source"
                  value={ind.source?.type ?? 'price'}
                  onChange={(e) => update(idx, { source: { ...(ind.source || {}), type: e.target.value as any } })}
                  options={[
                    { value: 'price', label: 'Price' },
                    { value: 'ohlcv', label: 'OHLCV' },
                    { value: 'indicator', label: 'Indicator' },
                  ]}
                />
                <Input
                  label="Source Field / Ref"
                  value={ind.source?.type === 'indicator' ? ind.source?.ref ?? '' : ind.source?.field ?? 'close'}
                  onChange={(e) => {
                    const v = e.target.value;
                    if ((ind.source?.type ?? 'price') === 'indicator') {
                      update(idx, { source: { type: 'indicator', ref: v } });
                    } else {
                      update(idx, { source: { type: ind.source?.type ?? 'price', field: v } });
                    }
                  }}
                  placeholder={ind.source?.type === 'indicator' ? 'ref indicator id' : 'close'}
                />
                <Select
                  label="Timeframe"
                  value={ind.timeframe ?? '1d'}
                  onChange={(e) => update(idx, { timeframe: e.target.value as Timeframe })}
                  options={timeframes}
                />
              </div>

              <div className="mt-3">
                <div className="mb-1 text-xs font-medium text-gray-700">Params</div>
                {(ind.params || []).map((p, pIdx) => (
                  <div key={pIdx} className="mb-2 grid grid-cols-1 gap-2 md:grid-cols-[1fr_1fr_auto]">
                    <Input
                      placeholder="key"
                      value={p.key}
                      onChange={(e) => updateParam(idx, pIdx, { key: e.target.value })}
                    />
                    <Input
                      placeholder="value"
                      value={String(p.value ?? '')}
                      onChange={(e) => {
                        const valText = e.target.value;
                        const tryNum = Number(valText);
                        updateParam(idx, pIdx, { value: isNaN(tryNum) ? valText : tryNum });
                      }}
                    />
                    <div className="flex items-center">
                      <Button variant="ghost" size="sm" onClick={() => removeParam(idx, pIdx)}>
                        Remove
                      </Button>
                    </div>
                  </div>
                ))}
                <Button variant="secondary" size="sm" onClick={() => addParam(idx)}>
                  Add Param
                </Button>
              </div>

              <div className="mt-3 flex justify-end">
                <Button variant="ghost" size="sm" onClick={() => remove(idx)}>
                  Remove Indicator
                </Button>
              </div>
            </div>
          ))}
        </div>
        {errors.length > 0 && (
          <div role="alert" className="mt-3 rounded-md bg-red-50 p-2 text-sm text-red-700">
            {errors.map((e, i) => (
              <div key={i}>{e}</div>
            ))}
          </div>
        )}
        <div className="mt-4">
          <Button onClick={add}>Add Indicator</Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default React.memo(StepIndicators);