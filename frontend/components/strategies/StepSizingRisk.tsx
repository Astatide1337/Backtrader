import React from 'react';
import Card, { CardContent, CardHeader } from 'components/ui/Card';
import Input from 'components/ui/Input';
import Select from 'components/ui/Select';
import type { StrategySchemaV1, SizingMode, SizingConfig } from 'types/strategySchema';

type Props = {
  value: StrategySchemaV1['sizing'];
  onChange: (v: StrategySchemaV1['sizing']) => void;
};

const sizingModes: { value: SizingMode; label: string }[] = [
  { value: 'fixed', label: 'Fixed Quantity' },
  { value: 'percent_of_equity', label: '% of Equity' },
  { value: 'volatility', label: 'Volatility-based' },
];

const StepSizingRisk: React.FC<Props> = ({ value, onChange }) => {
  const [sizing, setSizing] = React.useState<SizingConfig>(value);

  React.useEffect(() => setSizing(value), [value]);

  function commit(next: SizingConfig) {
    setSizing(next);
    onChange(next);
  }

  function updateMode(mode: SizingMode) {
    const next: SizingConfig = { ...sizing, mode };
    // set default params per mode
    if (mode === 'fixed') {
      next.params = { quantity: Number((sizing.params as any)?.quantity ?? 1) };
    } else if (mode === 'percent_of_equity') {
      next.params = { percent: Number((sizing.params as any)?.percent ?? 1) };
    } else if (mode === 'volatility') {
      next.params = { atrPeriod: Number((sizing.params as any)?.atrPeriod ?? 14), riskPct: Number((sizing.params as any)?.riskPct ?? 1) };
    }
    commit(next);
  }

  function updateParam(key: string, val: number | string) {
    const params = { ...(sizing.params || {}) };
    params[key] = val;
    commit({ ...sizing, params });
  }

  function updateRisk(key: 'maxPositions' | 'stopLossPct' | 'takeProfitPct' | 'trailingStopPct', val: number) {
    const risk = { ...(sizing.risk || {}) };
    (risk as any)[key] = val;
    commit({ ...sizing, risk });
  }

  const params = sizing.params || {};

  return (
    <Card>
      <CardHeader>
        <h2 className="text-base font-semibold text-gray-900">Sizing & Risk</h2>
        <p className="mt-1 text-sm text-gray-600">Configure position sizing and basic risk controls.</p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <Select
            label="Sizing Mode"
            value={sizing.mode}
            onChange={(e) => updateMode(e.target.value as SizingMode)}
            options={sizingModes}
          />
          {sizing.mode === 'fixed' && (
            <Input
              label="Quantity"
              type="number"
              value={String((params as any).quantity ?? 1)}
              onChange={(e) => updateParam('quantity', Number(e.target.value))}
              placeholder="1"
            />
          )}
          {sizing.mode === 'percent_of_equity' && (
            <Input
              label="% of Equity"
              type="number"
              value={String((params as any).percent ?? 1)}
              onChange={(e) => updateParam('percent', Number(e.target.value))}
              placeholder="1"
            />
          )}
          {sizing.mode === 'volatility' && (
            <>
              <Input
                label="ATR Period"
                type="number"
                value={String((params as any).atrPeriod ?? 14)}
                onChange={(e) => updateParam('atrPeriod', Number(e.target.value))}
              />
              <Input
                label="Risk %"
                type="number"
                value={String((params as any).riskPct ?? 1)}
                onChange={(e) => updateParam('riskPct', Number(e.target.value))}
              />
            </>
          )}
        </div>

        <div className="mt-6">
          <h3 className="text-sm font-semibold text-gray-900">Risk Controls</h3>
          <div className="mt-2 grid grid-cols-1 gap-4 md:grid-cols-4">
            <Input
              label="Max Positions"
              type="number"
              value={String(value.risk?.maxPositions ?? 5)}
              onChange={(e) => updateRisk('maxPositions', Number(e.target.value))}
            />
            <Input
              label="Stop Loss % (0-1)"
              type="number"
              step="0.01"
              value={String(value.risk?.stopLossPct ?? '')}
              onChange={(e) => updateRisk('stopLossPct', Number(e.target.value))}
            />
            <Input
              label="Take Profit % (0-1)"
              type="number"
              step="0.01"
              value={String(value.risk?.takeProfitPct ?? '')}
              onChange={(e) => updateRisk('takeProfitPct', Number(e.target.value))}
            />
            <Input
              label="Trailing Stop % (0-1)"
              type="number"
              step="0.01"
              value={String(value.risk?.trailingStopPct ?? '')}
              onChange={(e) => updateRisk('trailingStopPct', Number(e.target.value))}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default React.memo(StepSizingRisk);