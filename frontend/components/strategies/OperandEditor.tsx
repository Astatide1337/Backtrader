import React from 'react';
import Select from 'components/ui/Select';
import Input from 'components/ui/Input';
import type { Operand } from 'types/strategySchema';

function OperandEditor({
  value,
  onChange,
  label,
}: {
  value: Operand;
  onChange: (o: Operand) => void;
  label: string;
}) {
  const kind = value.kind;
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-gray-700">{label}</label>
      <div className="grid grid-cols-1 gap-2 md:grid-cols-3">
        <Select
          value={kind}
          onChange={(e) => {
            const k = e.target.value as Operand['kind'];
            if (k === 'const') onChange({ kind: 'const', value: 0 });
            else if (k === 'indicator') onChange({ kind: 'indicator', ref: '' });
            else if (k === 'price') onChange({ kind: 'price', field: 'close' });
            else onChange({ kind: 'expr', expr: '' });
          }}
          options={[
            { value: 'const', label: 'Constant' },
            { value: 'indicator', label: 'Indicator' },
            { value: 'price', label: 'Price' },
            { value: 'expr', label: 'Expression' },
          ]}
        />
        {value.kind === 'const' && (
          <Input
            placeholder="value"
            value={String(value.value ?? '')}
            onChange={(e) => {
              const text = e.target.value;
              const maybeNum = Number(text);
              onChange({ ...value, kind: 'const', value: isNaN(maybeNum) ? text : maybeNum });
            }}
          />
        )}
        {value.kind === 'indicator' && (
          <Input
            placeholder="indicator id"
            value={value.ref ?? ''}
            onChange={(e) => onChange({ ...value, kind: 'indicator', ref: e.target.value })}
          />
        )}
        {value.kind === 'price' && (
          <Select
            value={value.field ?? 'close'}
            onChange={(e) => onChange({ ...value, kind: 'price', field: e.target.value as Extract<Operand, { kind: 'price' }>['field'] })}
            options={[
              { value: 'open', label: 'Open' },
              { value: 'high', label: 'High' },
              { value: 'low', label: 'Low' },
              { value: 'close', label: 'Close' },
              { value: 'volume', label: 'Volume' },
            ]}
          />
        )}
        {value.kind === 'expr' && (
          <Input
            placeholder="expr: e.g., (rsi14 < 30) ? 1 : 0"
            value={value.expr ?? ''}
            onChange={(e) => onChange({ ...value, kind: 'expr', expr: e.target.value })}
          />
        )}
      </div>
    </div>
  );
}

export default OperandEditor;
