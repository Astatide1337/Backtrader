import React from 'react';
import Card, { CardContent, CardHeader } from 'components/ui/Card';
import Select from 'components/ui/Select';
import Input from 'components/ui/Input';
import Button from 'components/ui/Button';
import type {
  StrategySchemaV1,
  ExitRules,
  ConditionGroup,
  Condition,
  Comparator,
  Operand,
  RuleSide,
} from 'types/strategySchema';
import { validateConditions } from 'types/strategySchema';

type Props = {
  value: StrategySchemaV1['exit'];
  onChange: (v: StrategySchemaV1['exit']) => void;
};

const comparators: { value: Comparator; label: string }[] = [
  { value: 'gt', label: '>' },
  { value: 'gte', label: '>=' },
  { value: 'lt', label: '<' },
  { value: 'lte', label: '<=' },
  { value: 'eq', label: '==' },
  { value: 'neq', label: '!=' },
  { value: 'crosses_above', label: 'crosses above' },
  { value: 'crosses_below', label: 'crosses below' },
];

function newCondition(): Condition {
  return {
    left: { kind: 'indicator', ref: '' },
    op: 'lt',
    right: { kind: 'const', value: 0 },
  };
}

function newGroup(): ConditionGroup {
  return { op: 'AND', conditions: [newCondition()] };
}

const StepExitRules: React.FC<Props> = ({ value, onChange }) => {
  const [exit, setExit] = React.useState<ExitRules>(value || { side: 'both', groups: [] });
  const [errors, setErrors] = React.useState<string[]>([]);

  React.useEffect(() => setExit(value || { side: 'both', groups: [] }), [value]);

  function commit(next: ExitRules) {
    setExit(next);
    onChange(next);
    // Exit rules can be empty, so validate only when groups exist
    if (next.groups && next.groups.length > 0) {
      setErrors(validateConditions(next.groups));
    } else {
      setErrors([]);
    }
  }

  function updateSide(side: RuleSide) {
    commit({ ...exit, side });
  }

  function addGroup() {
    commit({ ...exit, groups: [...(exit.groups || []), newGroup()] });
  }

  function removeGroup(idx: number) {
    const groups = (exit.groups || []).filter((_, i) => i !== idx);
    commit({ ...exit, groups });
  }

  function addCondition(gIdx: number) {
    const groups = (exit.groups || []).map((g, i) =>
      i === gIdx ? { ...g, conditions: [...(g.conditions || []), newCondition()] } : g,
    );
    commit({ ...exit, groups });
  }

  function removeCondition(gIdx: number, cIdx: number) {
    const groups = (exit.groups || []).map((g, i) =>
      i === gIdx ? { ...g, conditions: g.conditions.filter((_, j) => j !== cIdx) } : g,
    );
    commit({ ...exit, groups });
  }

  function updateGroupOp(gIdx: number, op: 'AND' | 'OR') {
    const groups = (exit.groups || []).map((g, i) => (i === gIdx ? { ...g, op } : g));
    commit({ ...exit, groups });
  }

  function updateCondition(gIdx: number, cIdx: number, patch: Partial<Condition>) {
    const groups = (exit.groups || []).map((g, i) => {
      if (i !== gIdx) return g;
      const conditions = g.conditions.map((c, j) => (j === cIdx ? { ...c, ...patch } : c));
      return { ...g, conditions };
    });
    commit({ ...exit, groups });
  }

  function OperandEditor({
    value,
    onChange,
    label,
  }: {
    value: Operand;
    onChange: (o: Operand) => void;
    label: string;
  }) {
    const kind = (value as any)?.kind ?? 'const';
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
          {kind === 'const' && (
            <Input
              placeholder="value"
              value={String((value as any).value ?? '')}
              onChange={(e) => {
                const text = e.target.value;
                const maybeNum = Number(text);
                onChange({ kind: 'const', value: isNaN(maybeNum) ? text : maybeNum });
              }}
            />
          )}
          {kind === 'indicator' && (
            <Input
              placeholder="indicator id"
              value={(value as any).ref ?? ''}
              onChange={(e) => onChange({ kind: 'indicator', ref: e.target.value })}
            />
          )}
          {kind === 'price' && (
            <Select
              value={(value as any).field ?? 'close'}
              onChange={(e) => onChange({ kind: 'price', field: e.target.value as any })}
              options={[
                { value: 'open', label: 'Open' },
                { value: 'high', label: 'High' },
                { value: 'low', label: 'Low' },
                { value: 'close', label: 'Close' },
                { value: 'volume', label: 'Volume' },
              ]}
            />
          )}
          {kind === 'expr' && (
            <Input
              placeholder="expr"
              value={(value as any).expr ?? ''}
              onChange={(e) => onChange({ kind: 'expr', expr: e.target.value })}
            />
          )}
        </div>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <h2 className="text-base font-semibold text-gray-900">Exit Rules</h2>
        <p className="mt-1 text-sm text-gray-600">Optional exit conditions. Leave empty to only use stops/targets.</p>
      </CardHeader>
      <CardContent>
        <div className="mb-3 max-w-xs">
          <Select
            label="Side"
            value={exit.side}
            onChange={(e) => updateSide(e.target.value as RuleSide)}
            options={[
              { value: 'long', label: 'Long' },
              { value: 'short', label: 'Short' },
              { value: 'both', label: 'Both' },
            ]}
          />
        </div>

        <div className="space-y-4">
          {(exit.groups || []).map((g, gIdx) => (
            <div key={gIdx} className="rounded-md border p-3">
              <div className="mb-2 flex items-center justify-between">
                <Select
                  value={g.op}
                  onChange={(e) => updateGroupOp(gIdx, e.target.value as any)}
                  options={[
                    { value: 'AND', label: 'AND group' },
                    { value: 'OR', label: 'OR group' },
                  ]}
                />
                <Button variant="ghost" size="sm" onClick={() => removeGroup(gIdx)}>
                  Remove Group
                </Button>
              </div>
              <div className="space-y-3">
                {g.conditions.map((c, cIdx) => (
                  <div key={cIdx} className="rounded-md bg-gray-50 p-3">
                    <div className="grid grid-cols-1 gap-2 md:grid-cols-[1fr_auto_1fr_auto] md:items-center">
                      <OperandEditor
                        label="Left"
                        value={c.left}
                        onChange={(o) => updateCondition(gIdx, cIdx, { left: o })}
                      />
                      <Select
                        value={c.op}
                        onChange={(e) => updateCondition(gIdx, cIdx, { op: e.target.value as Comparator })}
                        options={comparators}
                      />
                      <OperandEditor
                        label="Right"
                        value={c.right}
                        onChange={(o) => updateCondition(gIdx, cIdx, { right: o })}
                      />
                      <div className="flex justify-end">
                        <Button variant="ghost" size="sm" onClick={() => removeCondition(gIdx, cIdx)}>
                          Remove
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
                <Button variant="secondary" size="sm" onClick={() => addCondition(gIdx)}>
                  Add Condition
                </Button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4">
          <Button onClick={addGroup}>Add Group</Button>
        </div>

        {errors.length > 0 && (
          <div role="alert" className="mt-3 rounded-md bg-amber-50 p-2 text-sm text-amber-800">
            {errors.map((e, i) => (
              <div key={i}>{e}</div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default React.memo(StepExitRules);