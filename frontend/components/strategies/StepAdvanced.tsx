import React from 'react';
import Card, { CardContent, CardHeader } from 'components/ui/Card';
import Input from 'components/ui/Input';
import Button from 'components/ui/Button';
import type { StrategySchemaV1, AdvancedExpression } from 'types/strategySchema';

type Props = {
  value: StrategySchemaV1['advanced'];
  onChange: (v: StrategySchemaV1['advanced']) => void;
};

function lintExpr(expr: string): string | null {
  if (!expr.trim()) return 'Expression cannot be empty.';
  // very lightweight lint: unmatched parentheses count
  const open = (expr.match(/\(/g) || []).length;
  const close = (expr.match(/\)/g) || []).length;
  if (open !== close) return 'Unmatched parentheses.';
  return null;
}

const StepAdvanced: React.FC<Props> = ({ value, onChange }) => {
  const [items, setItems] = React.useState<AdvancedExpression[]>(value?.expressions || []);
  const [errors, setErrors] = React.useState<Record<string, string | null>>({});

  React.useEffect(() => setItems(value?.expressions || []), [value]);

  function commit(nextList: AdvancedExpression[]) {
    setItems(nextList);
    onChange({ ...(value || {}), expressions: nextList });
    // recompute lint
    const errs: Record<string, string | null> = {};
    for (const it of nextList) {
      errs[it.id] = lintExpr(it.expr);
    }
    setErrors(errs);
  }

  function add() {
    const id = `adv_${Date.now()}`;
    commit([...(items || []), { id, expr: '' }]);
  }

  function remove(idx: number) {
    commit(items.filter((_, i) => i !== idx));
  }

  function update(idx: number, patch: Partial<AdvancedExpression>) {
    const next = items.map((it, i) => (i === idx ? { ...it, ...patch } : it));
    commit(next);
  }

  return (
    <Card>
      <CardHeader>
        <h2 className="text-base font-semibold text-gray-900">Advanced (optional)</h2>
        <p className="mt-1 text-sm text-gray-600">Custom expressions used within conditions or as helpers.</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {items.length === 0 && <p className="text-sm text-gray-600">No advanced expressions added.</p>}
          {items.map((it, idx) => (
            <div key={it.id} className="rounded-md border p-3">
              <div className="grid grid-cols-1 gap-3 md:grid-cols-[1fr_auto]">
                <Input
                  label="Identifier"
                  value={it.id}
                  onChange={(e) => update(idx, { id: e.target.value })}
                  placeholder="unique id"
                />
                <div className="flex items-end">
                  <Button variant="ghost" size="sm" onClick={() => remove(idx)}>
                    Remove
                  </Button>
                </div>
              </div>
              <div className="mt-2">
                <label htmlFor={`expr_${idx}`} className="mb-1 block text-sm font-medium text-gray-700">
                  Expression
                </label>
                <textarea
                  id={`expr_${idx}`}
                  className="input min-h-[80px] w-full font-mono text-xs"
                  value={it.expr}
                  onChange={(e) => update(idx, { expr: e.target.value })}
                  placeholder="e.g., rsi14 < 30"
                />
                {errors[it.id] && <div className="mt-1 text-xs text-amber-700">{errors[it.id]}</div>}
              </div>
            </div>
          ))}
        </div>
        <div className="mt-3">
          <Button onClick={add}>Add Expression</Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default React.memo(StepAdvanced);